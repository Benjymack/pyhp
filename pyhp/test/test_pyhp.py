# pylint: disable=missing-function-docstring

from unittest import TestCase

from pyhp.text_processing import remove_initial_indentation, prepare_code_text
from pyhp.file_processing import parse_html
from pyhp.code_execution import prepare_globals_locals, run_parsed_code
from pyhp.cookies import NewCookie
from pyhp.pyhp import PyhpProtocol


class TestPyhpRunCodeText(TestCase):
    pass


class TestPyhpRemoveInitialIndentation(TestCase):
    def test_no_indentation(self):
        cases = (
            '',
            "print('Hello')",
            '''if True:
    print('True')
else:
    print('False')''',
            'foo = [x**x for x in range(10)]',
            '''print('<pyhp>print("Hello")</pyhp>')''',
        )

        for string in cases:
            self.assertEqual(remove_initial_indentation(string), string)

    def test_indented(self):
        cases = (
            (' x = 1', 'x = 1'),
            ('    print(1)', 'print(1)'),
            ('\tprint(2)', 'print(2)'),
        )  # TODO: More cases

        for indented, unindented in cases:
            self.assertEqual(remove_initial_indentation(indented), unindented)

    def test_less_indentation_in_subsequent_lines_than_first_line(self):
        error_cases = [
            '    print(1)\nprint(2)',
            '  x=1\n x=2',
            '\t\tprint(2)\n\t\tprint(3)\n\tprint(5)',
        ]  # TODO: More cases
        no_error_cases = [
            '    if True:\n        print(1)\n\n        print(2)',
            ' print(1)\n\n\n print(2)',
        ]

        for case in error_cases:
            self.assertRaises(SyntaxError, remove_initial_indentation, case)
        for case in no_error_cases:
            remove_initial_indentation(case)

    def test_multiline_string_indentation(self):
        pass  # TODO: Finish


class TestPyhpPrepareCodeText(TestCase):
    def test_extra_newlines(self):
        cases = [
            ('x = 1\n\n', 'x = 1'),
            ('\n\nx = 1\n\n', 'x = 1'),
            ('\n\nx = 1\n\n\n', 'x = 1'),
            ('print("Hello\\nWorld")', 'print("Hello\\nWorld")'),
            ('print("Hello")\nprint("World")',
             'print("Hello")\nprint("World")'),
        ]

        for input_code, output in cases:
            self.assertEqual(prepare_code_text(input_code), output)


class TestPyhpPrepareGlobalsLocals(TestCase):
    def test_typical_globals(self):
        pyhp_class = MockPyhp()
        self.assertEqual(prepare_globals_locals(pyhp_class),
                         ({'pyhp': pyhp_class}, {}))
        self.assertIs(prepare_globals_locals(pyhp_class)[0]['pyhp'], pyhp_class)


class TestPyhpRunParsedCode(TestCase):
    def test_normal_html(self):
        cases = [
            '<p>Hello</p>',
            'Hi',
            '<div>Hello</div>',
        ]

        for case in cases:
            mock_pyhp = MockPyhp()
            self.assertEqual(run_parsed_code(parse_html(case), mock_pyhp), case)

    def test_blank_pyhp_tags(self):
        cases = [
            '<pyhp></pyhp>',
            '<pyhp> </pyhp>',
            '<pyhp>\n</pyhp>',
            '<pyhp>\n\n</pyhp>',
            '<pyhp></pyhp><pyhp></pyhp>',
        ]

        for case in cases:
            mock_pyhp = MockPyhp()
            self.assertEqual(run_parsed_code(parse_html(case), mock_pyhp), '')

    def test_print_statement(self):
        cases = [
            ("<pyhp>print('Hello', end='')</pyhp>", 'Hello'),
            ("<pyhp>print('Hello', end=' ')\nprint('World', end='')</pyhp>",
             'Hello World'),
        ]

        for input_code, expected in cases:
            mock_pyhp = MockPyhp()
            self.assertEqual(run_parsed_code(parse_html(input_code), mock_pyhp),
                             expected)

    def test_get_cookies(self):
        pass  # TODO: Finish

    def test_set_cookies(self):
        cases = [
            ("<pyhp>pyhp.set_cookie('foo', 'bar')</pyhp>",
             {'foo': NewCookie('foo', 'bar')}),
        ]

        for case in cases:
            dom = parse_html(case[0])
            # TODO: Finish

    def test_get_parameters(self):
        pass  # TODO: Finish

    def test_post_parameters(self):
        pass  # TODO: Finish

    def test_include(self):
        pass  # TODO: Finish

    def test_run_error_code_with_debug(self):
        pass  # TODO: Finish

    def test_run_error_code_without_debug(self):
        pass  # TODO: Finish


class TestPyhpFileProcessing(TestCase):
    pass


class MockPyhp(PyhpProtocol):
    def __init__(self, debug: bool = False):
        self._debug = debug

    @property
    def debug(self):
        return self._debug
