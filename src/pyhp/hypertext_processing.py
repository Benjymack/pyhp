"""
Sets up functions for processing DOMs and hypertext.
"""

# pylint: disable=missing-function-docstring

from bs4 import BeautifulSoup, Tag
from bs4.element import ResultSet

PYHP_TAG = 'pyhp'


def get_code_blocks(dom: BeautifulSoup) -> ResultSet[Tag]:
    return dom.select(f'{PYHP_TAG}:not({PYHP_TAG} *)')


def parse_text(text: str) -> BeautifulSoup:
    return BeautifulSoup(text, 'html.parser')
