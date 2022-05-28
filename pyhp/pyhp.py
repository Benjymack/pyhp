# Imports
from typing import Optional
from argparse import ArgumentParser

import markupsafe

try:
    from pyhp.file_processing import get_absolute_path, load_file, get_directory
    from pyhp.code_execution import run_parsed_code
    from pyhp.cookies import NewCookie, DeleteCookie
except ImportError:
    from file_processing import get_absolute_path, load_file, get_directory
    from code_execution import run_parsed_code
    from cookies import NewCookie, DeleteCookie


__all__ = ['load_file', 'run_parsed_code', 'get_absolute_path', 'Pyhp',
           'PyhpProtocol']


class PyhpProtocol:
    @property
    def debug(self):
        raise NotImplementedError


class Pyhp(PyhpProtocol):
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

        self._new_cookies: dict[str, NewCookie] = {}
        self._to_delete_cookies: dict[str, DeleteCookie] = {}

        self._redirect_info: Optional[(str, int)] = None

    def include(self, relative_path: str):
        absolute_path = get_absolute_path(relative_path, self._current_dir)

        pyhp_class = Pyhp(get_directory(absolute_path), self._debug,
                          self._cookies, self._get, self._post)

        output = run_parsed_code(load_file(absolute_path), pyhp_class)

        print(output, end='')

    def redirect(self, url: str, status_code: int = 302):
        self._redirect_info = (url, status_code)

    def get_redirect_information(self) -> Optional[tuple[str, int]]:
        return self._redirect_info

    def set_cookie(self, key: str, **kwargs):
        self._new_cookies[key] = NewCookie(key, **kwargs)

    def delete_cookie(self, key: str, **kwargs):
        self._to_delete_cookies[key] = DeleteCookie(key, **kwargs)

    def get_new_cookies(self):
        return self._new_cookies

    def get_delete_cookies(self):
        return self._to_delete_cookies

    @staticmethod
    def escape(text: str):
        return markupsafe.escape(text)

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
