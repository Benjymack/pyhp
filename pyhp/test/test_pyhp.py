"""
Tests PyHP separate from any server.

TestPyhpRemoveInitialIndentation:
    Tests that the initial indentation is correctly removed.
TestPyhpPrepareCodeText:
    Tests that the code text is correctly prepared
    (excess newlines removed, etc)
TestPyhpPrepareGlobalsLocals:
    Tests that the globals and locals contain the required information.
TestPyhpRunParsedCode:
    Tests that the code is correctly run, including cookies, GET, POST.
TestPyhpFileProcessing:
    Tests that PyHP can load and execute files.
"""

# pylint: disable=missing-function-docstring

from unittest import TestCase
from datetime import datetime
from pathlib import PurePath

from mocks import MockFileProcessor

from pyhp.text_processing import remove_initial_indentation, prepare_code_text
from pyhp.hypertext_processing import parse_text
from pyhp.code_execution import prepare_globals_locals, run_parsed_code
from pyhp.cookies import NewCookie
from pyhp.pyhp import Pyhp


class TestPyhpRemoveInitialIndentation(TestCase):
    """Tests that the initial indentation is correctly removed."""
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
            self.assertEqual(string, remove_initial_indentation(string))

    def test_indented(self):
        cases = (
            (' x = 1', 'x = 1'),
            ('    print(1)', 'print(1)'),
            ('\tprint(2)', 'print(2)'),
            ('\t  print(3)', 'print(3)'),
            ('\t    if True:\n\t        print(1)', 'if True:\n    print(1)'),
        )

        for indented, unindented in cases:
            self.assertEqual(unindented, remove_initial_indentation(indented))

    def test_less_indentation_in_subsequent_lines_than_first_line(self):
        error_cases = [
            '    print(1)\nprint(2)',
            '  x=1\n x=2',
            '\t\tprint(2)\n\t\tprint(3)\n\tprint(5)',
        ]
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
    """
    Tests that the code text is correctly prepared
    (excess newlines removed, etc)
    """
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
    """Tests that the globals and locals contain the required information."""
    def test_typical_globals(self):
        file_processor = MockFileProcessor()
        pyhp_class = Pyhp(PurePath(), file_processor)
        self.assertEqual(prepare_globals_locals(pyhp_class),
                         ({'pyhp': pyhp_class}, {}))
        self.assertIs(prepare_globals_locals(pyhp_class)[0]['pyhp'], pyhp_class)


class TestPyhpRunParsedCode(TestCase):
    """Tests that the code is correctly run, including cookies, GET, POST."""
    def test_normal_html(self):
        cases = [
            '<p>Hello</p>',
            'Hi',
            '<div>Hello</div>',
        ]

        for case in cases:
            self.assertEqual(create_file_processor_and_run_code(case), case)

    def test_blank_pyhp_tags(self):
        cases = [
            '<pyhp></pyhp>',
            '<pyhp> </pyhp>',
            '<pyhp>\n</pyhp>',
            '<pyhp>\n\n</pyhp>',
            '<pyhp></pyhp><pyhp></pyhp>',
        ]

        for case in cases:
            self.assertEqual(create_file_processor_and_run_code(case), '')

    def test_print_statement(self):
        cases = [
            ("<pyhp>print('Hello', end='')</pyhp>", 'Hello'),
            ("<pyhp>print('Hello', end=' ')\nprint('World', end='')</pyhp>",
             'Hello World'),
        ]

        for input_code, expected in cases:
            self.assertEqual(create_file_processor_and_run_code(input_code),
                             expected)

    def test_get_cookies(self):
        pass  # TODO: Finish

    def test_set_cookies(self):
        cases = [
            ("<pyhp>pyhp.set_cookie('foo', value='bar')</pyhp>",
             {'foo': NewCookie('foo', 'bar')}),
            ("<pyhp>pyhp.set_cookie('foo', value='bar', max_age=10)</pyhp>",
             {'foo': NewCookie('foo', 'bar', max_age=10)}),
            ("<pyhp>from datetime import datetime, timedelta\n"
             "pyhp.set_cookie('foo', value='bar', "
             "max_age=10, expires=datetime(2030, 1, 1))</pyhp>",
             {'foo': NewCookie('foo', 'bar', max_age=10,
                               expires=datetime(2030, 1, 1))}),
        ]

        for case in cases:
            file_processor = MockFileProcessor()
            pyhp_class = Pyhp(PurePath(), file_processor)
            run_parsed_code(parse_text(case[0]), pyhp_class)
            self.assertEqual(case[1], pyhp_class.get_new_cookies())

    def test_get_parameters(self):
        cases = [
            ("<pyhp>print(pyhp.get['foo'])</pyhp>", {'foo': 'bar'}, 'bar\n'),
            ("<pyhp>print(pyhp.get['foo'] + ' ' + pyhp.get['baz'])</pyhp>",
             {'foo': 'bar', 'baz': 'qux'}, 'bar qux\n'),
        ]

        for case in cases:
            file_processor = MockFileProcessor()
            pyhp_class = Pyhp(PurePath(), file_processor, get=case[1])
            self.assertEqual(run_parsed_code(parse_text(case[0]), pyhp_class),
                             case[2])

    def test_post_parameters(self):
        cases = [
            ("<pyhp>print(pyhp.post['foo'])</pyhp>", {'foo': 'bar'}, 'bar\n'),
            ("<pyhp>print(pyhp.post['foo'] + ' ' + pyhp.post['baz'])</pyhp>",
             {'foo': 'bar', 'baz': 'qux'}, 'bar qux\n'),
        ]

        for case in cases:
            file_processor = MockFileProcessor()
            pyhp_class = Pyhp(PurePath(), file_processor, post=case[1])
            self.assertEqual(run_parsed_code(parse_text(case[0]), pyhp_class),
                             case[2])

    def test_include(self):
        pass  # TODO: Finish

    def test_run_error_code(self):
        cases = [
            ('<pyhp>x = </pyhp>', 'SyntaxError: invalid syntax'),
            ('<pyhp>raise Exception()</pyhp>', 'Exception'),
            ('<pyhp>print(x)</pyhp>', "NameError: name 'x' is not defined"),
        ]

        for case in cases:
            file_processor = MockFileProcessor()
            dom = parse_text(case[0])

            # Run with debug
            pyhp_class = Pyhp(PurePath(), file_processor, debug=True)
            self.assertIn(case[1], run_parsed_code(dom, pyhp_class))

            # Run without debug
            pyhp_class = Pyhp(PurePath(), file_processor, debug=False)
            with self.assertRaises(RuntimeError):
                run_parsed_code(dom, pyhp_class)


class TestPyhpFileProcessing(TestCase):
    """Tests that PyHP can load and execute files."""
    def test_get_directory(self):
        pass  # TODO: Finish


def create_file_processor_and_run_code(case: str):
    file_processor = MockFileProcessor(case)
    pyhp_class = Pyhp(PurePath(), file_processor)
    return pyhp_class.include('index.pyhp')
