# Imports
from typing import Optional

from bs4 import BeautifulSoup
from io import StringIO
from contextlib import redirect_stdout
from copy import deepcopy

import traceback
import sys
import os


__all__ = ['load_file', 'run_code_block', 'run_parsed_code', 'include']


# Constants
TAG_NAME = 'pyhp'
FILE_EXTENSION = TAG_NAME
REMOVE_INITIAL_INDENTATION = True


# Functions
def load_file(file_path: str) -> BeautifulSoup:
    """
    Loads a pphp file and parses it, returning the BeautifulSoup object.
    """

    # Check if the pyhp file with that name exists
    if not os.path.exists(file_path):
        possible_path = f'{file_path}.{FILE_EXTENSION}'
        if os.path.exists(possible_path):
            file_path = possible_path
        else:
            raise FileNotFoundError(f'File not found: {file_path}')

    # Open and parse the file
    with open(file_path, 'r') as f:
        return BeautifulSoup(f.read(), 'html.parser')


def run_code_block(code_block: str,
                   globals_: dict,
                   locals_: dict) -> (bool, str):
    """
    Runs the code block, in the given globals and locals environment.
    Returns a tuple of (success, output).
    """
    output = StringIO()
    exception = None

    # Run the code
    try:
        with redirect_stdout(output):
            exec(code_block, globals_, locals_)
    except Exception:
        exception = traceback.format_exc()

    # Return the output of the code
    if exception is None:
        return True, output.getvalue()
    else:
        return False, f'<pre>{exception}</pre>'


def run_parsed_code(parsed_code: BeautifulSoup,
                    initial_globals: Optional[dict] = None,
                    debug: bool = False) -> str:
    """
    Runs the parsed pyhp code, returning the html output.
    """
    output_code = deepcopy(parsed_code)

    if initial_globals is None:
        globals_ = {}
    else:
        globals_ = initial_globals
    locals_ = {}

    code_blocks = output_code.select(f'{TAG_NAME}:not({TAG_NAME} *)')

    for code_block in code_blocks:
        code_text = code_block.decode_contents()
        # TODO: Check that stripping doesn't cause issues
        code_text = code_text.lstrip('\n').rstrip('\n')

        if REMOVE_INITIAL_INDENTATION:
            lines = code_text.split('\n')
            whitespace_characters = len(lines[0]) - len(lines[0].lstrip())
            # TODO: Check if there isn't enough whitespace
            #  (if we are removing actual characters)
            code_text = '\n'.join(line[whitespace_characters:]
                                  for line in lines)

        success, output = run_code_block(code_text,
                                         globals_, locals_)

        if not success and not debug:
            raise RuntimeError(output)

        code_block.replace_with(BeautifulSoup(output, 'html.parser'))

        if not success:
            break

    return str(output_code)


def include(file_path: str):
    """
    Include a pyhp file inside the current pyhp file.
    """
    print(run_parsed_code(load_file(file_path)), end='')
