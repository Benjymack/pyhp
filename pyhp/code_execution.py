from bs4 import BeautifulSoup
from io import StringIO
from contextlib import redirect_stdout
from copy import deepcopy
from traceback import format_exc
from typing import TYPE_CHECKING

try:
    from pyhp.text_processing import prepare_code_text
except ImportError:
    from text_processing import prepare_code_text


if TYPE_CHECKING:
    from pyhp import Pyhp


PYHP_TAG = 'pyhp'


def run_parsed_code(dom: BeautifulSoup,
                    pyhp_class: 'Pyhp') -> str:
    output_dom = deepcopy(dom)

    globals_, locals_ = prepare_globals_locals(pyhp_class)

    code_blocks = output_dom.select(f'{PYHP_TAG}:not({PYHP_TAG} *)')

    for code_block in code_blocks:
        code_text = prepare_code_text(code_block)

        success, output = run_code_text(code_text, globals_, locals_)

        if not success and not pyhp_class.debug:
            raise RuntimeError(output)

        code_block.replace_with(BeautifulSoup(output, 'html.parser'))

        if not success:
            break

    return str(output_dom)


def run_code_text(code_block: str,
                  globals_: dict,
                  locals_: dict) -> (bool, str):
    output_text = StringIO()

    try:
        with redirect_stdout(output_text):
            exec(code_block, globals_, locals_)
    except Exception:
        success = False
        output = f'<pre>{format_exc()}</pre>'
    else:
        success = True
        output = output_text.getvalue()

    return success, output


def prepare_globals_locals(pyhp_class: 'Pyhp') -> (dict, dict):
    globals_ = {'pyhp': pyhp_class}
    locals_ = {}

    return globals_, locals_
