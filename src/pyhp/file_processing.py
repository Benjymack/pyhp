"""
Sets up functions for loading and parsing PyHP files.
"""

# pylint: disable=missing-function-docstring

from pathlib import PurePath, Path


PYHP_FILE_EXTENSION = 'pyhp'


class FileProcessor:
    """
    Abstract class for interacting with the file system.
    """
    def get_file_contents(self, path: PurePath) -> str:
        raise NotImplementedError

    def is_dir(self, path: PurePath) -> bool:
        raise NotImplementedError

    def is_file(self, path: PurePath) -> bool:
        raise NotImplementedError

    def is_pyhp_file(self, path: PurePath) -> bool:
        return path.suffix == f'.{PYHP_FILE_EXTENSION}'

    def get_true_path(self, path: PurePath) -> PurePath:
        if self.is_dir(path):
            raise IsADirectoryError

        if self.is_file(path):
            return path

        path = path.with_suffix(f'{path.suffix}.{PYHP_FILE_EXTENSION}')

        if self.is_file(path):
            return path

        raise FileNotFoundError('Unable to find file.')

    def get_absolute_path(self, path: PurePath) -> Path:
        raise NotImplementedError  # TODO: This is less than ideal


class SystemFileProcessor(FileProcessor):
    """
    Implementation of the FileProcessor interface, for normal interation with
    system files and directories.
    """
    def __init__(self, base_dir: Path):
        if not base_dir.is_dir():
            raise FileNotFoundError('The base directory does not exist.')
        self._base_dir = base_dir

    def get_file_contents(self, path: PurePath) -> str:
        with open(self.get_absolute_path(path), 'r', encoding='utf-8') as file:
            return file.read()

    def is_dir(self, path: PurePath) -> bool:
        return self.get_absolute_path(path).is_dir()

    def is_file(self, path: PurePath) -> bool:
        return self.get_absolute_path(path).is_file()

    def get_absolute_path(self, path: PurePath) -> Path:
        absolute_path = (self._base_dir / path).resolve()
        if self._base_dir not in absolute_path.parents and \
                self._base_dir != absolute_path:
            raise RuntimeError(f'Path ({absolute_path}) is outside of base '
                               f'directory ({self._base_dir}).')
        return absolute_path
