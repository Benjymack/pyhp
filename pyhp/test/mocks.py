from typing import Union
from pathlib import PurePath

from pyhp.file_processing import FileProcessor


class MockFileProcessor(FileProcessor):
    def __init__(self, file_contents: Union[dict[PurePath, str], str] = ''):
        self._file_contents = file_contents

    def get_file_contents(self, path: PurePath) -> str:
        if isinstance(self._file_contents, dict):
            return self._file_contents[path]
        return self._file_contents

    def is_dir(self, path: PurePath) -> bool:
        raise NotImplementedError

    def is_file(self, path: PurePath) -> bool:
        raise NotImplementedError

    def is_pyhp_file(self, path: PurePath) -> bool:
        raise NotImplementedError
