# Imports
from typing import Optional

from bs4 import BeautifulSoup
from io import StringIO
from contextlib import redirect_stdout
from copy import deepcopy

import traceback
import os

__all__ = ['load_file', 'run_code_text', 'run_parsed_code', 'include']

# Constants
TAG_NAME = 'pyhp'
FILE_EXTENSION = TAG_NAME
REMOVE_INITIAL_INDENTATION = True


# Functions
def get_pyhp_file_path(path: str) -> str:
    if os.path.exists(path):
        return path
    else:
        possible_path = f'{path}.{FILE_EXTENSION}'
        if os.path.exists(possible_path):
            return possible_path
        else:
            raise FileNotFoundError(f'File not found: {path}')


def load_file(path: str) -> BeautifulSoup:
    """
    Loads a pphp file and parses it, returning the BeautifulSoup object.
    """

    file_path = get_pyhp_file_path(path)

    with open(file_path, 'r') as f:
        return BeautifulSoup(f.read(), 'html.parser')


def run_code_text(code_block: str,
                  globals_: dict,
                  locals_: dict) -> (bool, str):
    """
    Runs the code block, in the given globals and locals environment.
    Returns a tuple of (success, output).
    """
    output_text = StringIO()
    exception = None

    # Run the code
    try:
        with redirect_stdout(output_text):
            exec(code_block, globals_, locals_)

        success = True
        output = output_text.getvalue()
    except Exception:
        success = False
        output = f'<pre>{traceback.format_exc()}</pre>'

    return success, output


def remove_initial_indentation(code: str) -> str:
    lines = code.split('\n')
    whitespace_characters = len(lines[0]) - len(lines[0].lstrip())
    # TODO: Check if there isn't enough whitespace
    #  (if we are removing actual characters)
    return '\n'.join(line[whitespace_characters:] for line in lines)


def prepare_code_text(code_block) -> str:
    """
    Prepares a code block for execution.
    """
    code_text = code_block.decode_contents()
    # TODO: Check that stripping doesn't cause issues
    code_text = code_text.lstrip('\n').rstrip('\n')

    if REMOVE_INITIAL_INDENTATION:
        code_text = remove_initial_indentation(code_text)

    return code_text


def prepare_globals_locals(initial_globals: Optional[dict] = None)\
        -> (dict, dict):
    """
    Prepares the globals and locals for execution.
    """
    if initial_globals is None:
        globals_ = {}
    else:
        globals_ = initial_globals
    locals_ = {}

    return globals_, locals_


def run_parsed_code(dom: BeautifulSoup,
                    initial_globals: Optional[dict] = None,
                    debug: bool = False) -> str:
    """
    Runs the parsed pyhp code, returning the html output.
    """
    output_dom = deepcopy(dom)

    globals_, locals_ = prepare_globals_locals(initial_globals)

    code_blocks = output_dom.select(f'{TAG_NAME}:not({TAG_NAME} *)')

    for code_block in code_blocks:
        code_text = prepare_code_text(code_block)

        success, output = run_code_text(code_text, globals_, locals_)

        if not success and not debug:
            raise RuntimeError(output)

        code_block.replace_with(BeautifulSoup(output, 'html.parser'))

        if not success:
            break

    return str(output_dom)


def include(file_path: str):
    """
    Include a pyhp file inside the current pyhp file.
    """
    print(run_parsed_code(load_file(file_path)), end='')
