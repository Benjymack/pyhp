# pylint: disable=missing-function-docstring

import os

from bs4 import BeautifulSoup


PYHP_FILE_EXTENSION = 'pyhp'


def load_file(absolute_path: str) -> BeautifulSoup:
    file_path = get_pyhp_file_path(absolute_path)

    with open(file_path, 'r', encoding='utf-8') as file:
        return parse_html(file.read())


def parse_html(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, 'html.parser')


def get_pyhp_file_path(absolute_path: str) -> str:
    if os.path.exists(absolute_path):
        return absolute_path

    if os.path.isdir(absolute_path):
        return os.path.join(absolute_path, f'index.{PYHP_FILE_EXTENSION}')

    possible_path = f'{absolute_path}.{PYHP_FILE_EXTENSION}'
    if os.path.exists(possible_path):
        return possible_path

    raise FileNotFoundError(f'File not found: {absolute_path}')


def get_absolute_path(relative_path: str, base_dir: str) -> str:
    return os.path.join(base_dir, relative_path)


def get_directory(absolute_path: str) -> str:
    return os.path.dirname(absolute_path)
