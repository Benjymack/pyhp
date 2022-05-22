# Imports
from typing import Optional
from argparse import ArgumentParser

try:
    from pyhp.file_processing import get_absolute_path, load_file, get_directory
    from pyhp.code_execution import run_parsed_code
except ImportError:
    from file_processing import get_absolute_path, load_file, get_directory
    from code_execution import run_parsed_code


__all__ = ['load_file', 'run_parsed_code', 'get_absolute_path', 'Pyhp']


class Pyhp:
    def __init__(self, current_dir: str,
                 debug: bool,
                 cookies: Optional[dict[str, str]] = None,
                 get: Optional[dict[str, str]] = None,
                 post: Optional[dict[str, str]] = None):

        self._current_dir = current_dir
        self._debug = debug

        self._cookies = cookies or {}
        self._get = get or {}
        self._post = post or {}

    def include(self, relative_path: str):
        absolute_path = get_absolute_path(relative_path, self._current_dir)

        pyhp_class = Pyhp(get_directory(absolute_path), self._debug,
                          self._cookies, self._get, self._post)

        output = run_parsed_code(load_file(absolute_path), pyhp_class)

        print(output, end='')

    @property
    def current_dir(self):
        return self._current_dir

    @property
    def debug(self):
        return self._debug

    @property
    def cookies(self):
        return self._cookies

    @property
    def get(self):
        return self._get

    @property
    def post(self):
        return self._post


if __name__ == '__main__':
    parser = ArgumentParser(description='Python Hypertext Preprocessor (PyHP)')
    parser.add_argument('file', help='File to run')
    parser.add_argument('-d', '--debug', action='store_true', help='Debug mode',
                        default=False)

    args = parser.parse_args()

    pyhp_class = Pyhp(get_directory(args.file), args.debug)
    dom = load_file(args.file)
    output = run_parsed_code(dom, pyhp_class)
    print(output)
