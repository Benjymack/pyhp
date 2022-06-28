"""
Sets up functions for processing DOMs and hypertext.
"""

# pylint: disable=missing-function-docstring, too-few-public-methods

import re


PYHP_TAG = 'pyhp'
REGEX = re.compile(rf'<{PYHP_TAG}>([\S\s]*?)</{PYHP_TAG}>')


class UglySoup:
    """
    A regex-based parser for PyHP code blocks.

    Does NOT support nested PyHP code blocks
    (or printing </pyhp> tags within PyHP code blocks).
    """
    def __init__(self, html: str):
        self._sections: list[tuple[bool, str]] = []

        prev_end = 0

        for match in REGEX.finditer(html):
            self._sections.append((False, html[prev_end:match.start()]))
            self._sections.append((True, match.group(1)))
            prev_end = match.end()

        self._sections.append((False, html[prev_end:]))

    @property
    def sections(self):
        return self._sections
