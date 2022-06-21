"""
Interface for the PyHP programs.
"""

from typing import Optional
from pathlib import PurePath
from bs4 import BeautifulSoup
import markupsafe

try:
    from file_processing import FileProcessor
    from code_execution import run_parsed_code
    from cookies import NewCookie, DeleteCookie
    from hypertext_processing import parse_text
except ImportError:
    from .file_processing import FileProcessor
    from .code_execution import run_parsed_code
    from .cookies import NewCookie, DeleteCookie
    from .hypertext_processing import parse_text

__all__ = ['Pyhp']


class Pyhp:
    """
    The interface for the PyHP file to interact with the server,
    and the web page.
    """

    # pylint: disable=too-many-instance-attributes, too-many-arguments

    def __init__(self, current_dir: PurePath,
                 file_processor: FileProcessor,
                 debug: bool = False,
                 cookies: Optional[dict[str, str]] = None,
                 get: Optional[dict[str, str]] = None,
                 post: Optional[dict[str, str]] = None):
        self._current_dir = current_dir
        self._debug = debug
        self._file_processor = file_processor

        self._cookies: dict[str, str] = cookies or {}
        self._get: dict[str, str] = get or {}
        self._post: dict[str, str] = post or {}

        self._new_cookies: dict[str, NewCookie] = {}
        self._to_delete_cookies: dict[str, DeleteCookie] = {}

        self._redirect_info: Optional[(str, int)] = None

    def display(self, relative_path: str):
        """Include another pyhp file and print it."""
        print(self.include(relative_path), end='')

    def include(self, relative_path: str) -> str:
        """
        Include another pyhp file into the current one,
        and return the output HTML.
        """
        new_current_dir = (self._current_dir / PurePath(relative_path)).parent

        new_pyhp_class = Pyhp(new_current_dir, self._file_processor,
                              self._debug, self._cookies, self._get, self._post)

        return new_pyhp_class.run(relative_path)

    def run(self, relative_path: str) -> str:
        """
        Runs another pyhp file in the context of the current one,
        and return the output HTML.
        """
        return run_parsed_code(
            self._parse_file(PurePath(relative_path)),
            self,
            self._file_processor,
        )

    def _parse_file(self, relative_path: PurePath) -> BeautifulSoup:
        return parse_text(self._load_file(relative_path))

    def _load_file(self, relative_path: PurePath) -> str:
        path = self._current_dir / relative_path
        return self._file_processor.get_file_contents(path)

    def redirect(self, url: str, status_code: int = 302):
        """Redirect to another url."""
        self._redirect_info = (url, status_code)

    def get_redirect_information(self) -> Optional[tuple[str, int]]:
        """Return the redirect information if present."""
        return self._redirect_info

    def set_cookie(self, key: str, **kwargs):
        """Set a cookie."""
        self._new_cookies[key] = NewCookie(key, **kwargs)

    def delete_cookie(self, key: str, **kwargs):
        """Delete a cookie."""
        self._to_delete_cookies[key] = DeleteCookie(key, **kwargs)

    def get_new_cookies(self):
        """Return the cookies that will be set."""
        return self._new_cookies

    def get_delete_cookies(self):
        """Return the cookies that will be deleted."""
        return self._to_delete_cookies

    @staticmethod
    def escape(text: str) -> str:
        """Escape text for use in HTML."""
        return str(markupsafe.escape(text))

    @property
    def current_dir(self) -> PurePath:
        """Return the directory of the currently executing file."""
        return self._current_dir

    @property
    def debug(self) -> bool:
        """Return whether the app is in debug mode."""
        return self._debug

    @property
    def cookies(self) -> dict[str, str]:
        """Return the cookies."""
        return self._cookies

    @property
    def get(self) -> dict[str, str]:
        """Return the GET parameters."""
        return self._get

    @property
    def post(self) -> dict[str, str]:
        """Return the POST data."""
        return self._post
