"""
Sets up mock classes for the testing of the PyHP framework.
"""

from typing import Union
from pathlib import PurePath

from pyhp.file_processing import FileProcessor


class MockFileProcessor(FileProcessor):
    """
    A mock FileProcessor, for use when testing. Takes either a dictionary of
    file paths and contents, or a string, and returns the contents of the file
    at the given path.
    """
    def __init__(self, file_contents: Union[dict[PurePath, str], str] = ''):
        self._file_contents = file_contents

    def get_file_contents(self, path: PurePath) -> str:
        if isinstance(self._file_contents, dict):
            return self._file_contents[path]
        return self._file_contents

    def is_dir(self, path: PurePath) -> bool:
        raise NotImplementedError('Please implement is_dir for specific test.')

    def is_file(self, path: PurePath) -> bool:
        raise NotImplementedError('Please implement is_file for specific test.')

    def is_pyhp_file(self, path: PurePath) -> bool:
        raise NotImplementedError(
            'Please implement is_pyhp_file for specific test.')
