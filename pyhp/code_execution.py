from bs4 import BeautifulSoup, Tag
from bs4.element import ResultSet
from io import StringIO
from contextlib import redirect_stdout
from copy import deepcopy
from traceback import format_exc
from typing import TYPE_CHECKING, Any

try:
    from pyhp.text_processing import prepare_code_block
except ImportError:
    from text_processing import prepare_code_block


if TYPE_CHECKING:
    from .pyhp import PyhpProtocol

PYHP_TAG = 'pyhp'


def run_parsed_code(dom: BeautifulSoup,
                    pyhp_class: 'PyhpProtocol') -> str:
    output_dom = deepcopy(dom)
    code_blocks = get_code_blocks(output_dom)

    globals_, locals_ = prepare_globals_locals(pyhp_class)

    for code_block in code_blocks:
        success = run_code_block(code_block, globals_, locals_, pyhp_class)

        if not success:
            break

    return str(output_dom)


def run_code_block(code_block: Tag, globals_: dict[str, Any],
                   locals_: dict[str, Any], pyhp_class: 'PyhpProtocol') -> bool:
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
            exec(code_text, globals_, locals_)
    except Exception:
        success = False
        output = f'<pre>{format_exc()}</pre>'
    else:
        success = True
        output = output_text.getvalue()

    return success, output


def get_code_blocks(dom: BeautifulSoup) -> ResultSet[Tag]:
    return dom.select(f'{PYHP_TAG}:not({PYHP_TAG} *)')


def prepare_globals_locals(pyhp_class: 'PyhpProtocol') -> (dict[str, Any],
                                                           dict[str, Any]):
    globals_ = {'pyhp': pyhp_class}
    locals_ = {}

    return globals_, locals_
