"""
Sets up functions for executing PyHP code blocks and code text.
"""

# pylint: disable=missing-function-docstring

from io import StringIO
from contextlib import redirect_stdout
from traceback import format_exc
from typing import TYPE_CHECKING, Any

try:
    from text_processing import prepare_code_text
    from hypertext_processing import UglySoup
except ImportError:
    from .text_processing import prepare_code_text
    from .hypertext_processing import UglySoup

if TYPE_CHECKING:
    from .pyhp_interface import Pyhp


def run_parsed_code(dom: UglySoup, pyhp_class: 'Pyhp') -> str:
    output_text = []

    for section in dom.sections:
        success, output = run_section(section, pyhp_class)

        output_text.append(output)

        if not success:
            break

    return ''.join(output_text)


def run_section(section: tuple[bool, str],
                pyhp_class: 'Pyhp') -> (bool, str):
    is_pyhp_code, text = section

    if is_pyhp_code:
        success, output = run_code_text(prepare_code_text(text),
                                        pyhp_class.globals, pyhp_class.locals)

        if not success and not pyhp_class.debug:
            raise RuntimeError(output)

        return success, output

    return True, text


def run_code_text(code_text: str,
                  globals_: dict[str, Any],
                  locals_: dict[str, Any]) -> (bool, str):
    output_text = StringIO()

    try:
        with redirect_stdout(output_text):
            exec(code_text, globals_, locals_)  # pylint: disable=exec-used
    except Exception:  # pylint: disable=broad-except
        success = False
        output = f'{output_text.getvalue()}<pre>{format_exc()}</pre>'
    else:
        success = True
        output = output_text.getvalue()

    return success, output
