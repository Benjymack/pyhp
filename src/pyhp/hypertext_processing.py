"""
Sets up functions for processing DOMs and hypertext.
"""

# pylint: disable=missing-function-docstring, too-few-public-methods

from dataclasses import dataclass
import re


PYHP_TAG = 'pyhp'
REGEX = re.compile(rf'<{PYHP_TAG}>([\S\s]*?)</{PYHP_TAG}>')


@dataclass
class Section:
    """Represents a section of either hypertext or PyHP code."""
    is_pyhp_code: bool
    text: str


class UglySoup:
    """
    A regex-based parser for PyHP code blocks.

    Does NOT support nested PyHP code blocks
    (or printing </pyhp> tags within PyHP code blocks).
    """
    def __init__(self, html: str):
        self._sections: list[Section] = []

        prev_end = 0

        for match in REGEX.finditer(html):
            self._add_section(False, html[prev_end:match.start()])
            self._add_section(True, match.group(1))
            prev_end = match.end()

        self._add_section(False, html[prev_end:])

    def _add_section(self, is_pyhp_code: bool, text: str):
        if text:
            self._sections.append(Section(is_pyhp_code, text))

    @property
    def sections(self) -> list[Section]:
        return self._sections
