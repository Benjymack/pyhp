"""
Sets up functions for executing PyHP code blocks and code text.
"""

# pylint: disable=missing-function-docstring

from io import StringIO
from contextlib import redirect_stdout
from copy import deepcopy
from traceback import format_exc
from typing import TYPE_CHECKING, Any
import sys

from bs4 import BeautifulSoup, Tag

try:
    from text_processing import prepare_code_block
    from hypertext_processing import get_code_blocks
    from file_processing import FileProcessor
except ImportError:
    from .text_processing import prepare_code_block
    from .hypertext_processing import get_code_blocks
    from .file_processing import FileProcessor

if TYPE_CHECKING:
    from .pyhp_interface import Pyhp


def run_parsed_code(dom: BeautifulSoup,
                    pyhp_class: 'Pyhp',
                    file_processor: FileProcessor) -> str:
    output_dom = deepcopy(dom)
    code_blocks = get_code_blocks(output_dom)

    globals_, locals_ = prepare_context(pyhp_class, file_processor)

    for code_block in code_blocks:
        success = run_code_block(code_block, globals_, locals_, pyhp_class)

        if not success:
            break

    return str(output_dom)


def run_code_block(code_block: Tag, globals_: dict[str, Any],
                   locals_: dict[str, Any], pyhp_class: 'Pyhp') -> bool:
    code_text = prepare_code_block(code_block)

    success, output = run_code_text(code_text, globals_, locals_)

    if not success and not pyhp_class.debug:
        raise RuntimeError(output)

    code_block.replace_with(BeautifulSoup(output, 'html.parser'))

    return success


def run_code_text(code_text: str,
                  globals_: dict[str, Any],
                  locals_: dict[str, Any]) -> (bool, str):
    output_text = StringIO()

    try:
        with redirect_stdout(output_text):
            exec(code_text, globals_, locals_)  # pylint: disable=exec-used
    except Exception:  # pylint: disable=broad-except
        success = False
        output = f'<pre>{format_exc()}</pre>'
    else:
        success = True
        output = output_text.getvalue()

    return success, output


def prepare_context(pyhp_class: 'Pyhp',
                    file_processor: FileProcessor) -> (dict[str, Any],
                                                       dict[str, Any]):
    context_globals = {'pyhp': pyhp_class}
    context_locals = {}

    # TODO: This is potentially a security flaw
    current_dir = str(file_processor.get_absolute_path(pyhp_class.current_dir))

    if current_dir not in sys.path:
        sys.path.append(current_dir)

    return context_globals, context_locals
