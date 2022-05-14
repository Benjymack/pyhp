# Imports
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
REMOVE_INITIAL_INDENTATION = True


# Functions
def load_file(file_path: str) -> BeautifulSoup:
    
    with open(file_path, 'r') as f:
        return BeautifulSoup(f.read(), 'lxml')


def run_code_block(code_block: str,
                   globals_: dict,
                   locals_: dict) -> (bool, str):
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
        return False, exception


def run_parsed_code(parsed_code: BeautifulSoup) -> str:
    output_code = deepcopy(parsed_code)

    globals_ = {}
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

        if not success:
            sys.stderr.write(output)
            return ''

        code_block.replace_with(BeautifulSoup(output, 'html.parser'))

    return str(output_code)


def include(file_path: str):
    print(run_parsed_code(load_file(file_path)))
