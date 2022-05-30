from bs4 import BeautifulSoup

import os


PYHP_FILE_EXTENSION = 'pyhp'


def load_file(absolute_path: str) -> BeautifulSoup:
    file_path = get_pyhp_file_path(absolute_path)

    with open(file_path, 'r') as f:
        return parse_html(f.read())


def parse_html(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, 'html.parser')


def get_pyhp_file_path(absolute_path: str) -> str:
    if os.path.exists(absolute_path):
        return absolute_path
    elif os.path.isdir(absolute_path):
        return os.path.join(absolute_path, f'index.{PYHP_FILE_EXTENSION}')
    else:
        possible_path = f'{absolute_path}.{PYHP_FILE_EXTENSION}'
        if os.path.exists(possible_path):
            return possible_path
        else:
            raise FileNotFoundError(f'File not found: {absolute_path}')


def get_absolute_path(relative_path: str, base_dir: str) -> str:
    return os.path.join(base_dir, relative_path)


def get_directory(absolute_path: str) -> str:
    return os.path.dirname(absolute_path)
