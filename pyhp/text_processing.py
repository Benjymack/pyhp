from bs4 import Tag


def prepare_code_text(code_block: Tag) -> str:
    code_text = code_block.decode_contents()
    code_text = code_text.lstrip('\n').rstrip('\n')
    code_text = remove_initial_indentation(code_text)

    return code_text


def remove_initial_indentation(code_text: str) -> str:
    lines = code_text.split('\n')
    whitespace_characters = len(lines[0]) - len(lines[0].lstrip())

    new_lines = []
    for line in lines:
        if line[:whitespace_characters].isspace() or whitespace_characters == 0:
            new_lines.append(line[whitespace_characters:])
        else:
            raise SyntaxError('Invalid code block indentation. More '
                              'indentation was in the first line than in '
                              'subsequent lines.')

    return '\n'.join(new_lines)
