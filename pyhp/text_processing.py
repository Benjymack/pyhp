"""
Sets up functions for processing PyHP code blocks and code text.
"""

# pylint: disable=missing-function-docstring

from bs4 import Tag


def prepare_code_block(code_block: Tag) -> str:
    code_text = code_block.decode_contents()
    prepared_code_text = prepare_code_text(code_text)

    return prepared_code_text


def prepare_code_text(code_text: str) -> str:
    code_text = code_text.lstrip('\n').rstrip('\n')
    code_text = remove_initial_indentation(code_text)

    return code_text


def remove_initial_indentation(code_text: str) -> str:
    lines = code_text.split('\n')
    whitespace_characters = len(lines[0]) - len(lines[0].lstrip())

    new_lines = remove_whitespace_from_lines(lines, whitespace_characters)

    return '\n'.join(new_lines)


def remove_whitespace_from_lines(lines: list[str],
                                 whitespace_characters: int) -> list[str]:
    new_lines = []
    for line in lines:
        if can_remove_whitespace_from_line(line, whitespace_characters):
            new_lines.append(line[whitespace_characters:])
        else:
            raise SyntaxError('Invalid code block indentation. More '
                              'indentation was in the first line than in '
                              'subsequent lines.')

    return new_lines


def can_remove_whitespace_from_line(line: str,
                                    whitespace_characters: int) -> bool:
    return (line[:whitespace_characters].isspace() or
            whitespace_characters == 0 or
            line == '')
