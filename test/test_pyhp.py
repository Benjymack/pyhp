"""
Tests PyHP separate from any server.

TestPyhpRemoveInitialIndentation:
    Tests that the initial indentation is correctly removed.
TestPyhpPrepareCodeText:
    Tests that the code text is correctly prepared
    (excess newlines removed, etc)
TestPyhpPrepareContext:
    Tests that the context (globals and locals) contains the required
    information.
TestPyhpRunParsedCode:
    Tests that the code is correctly run, including cookies, GET, POST.
TestPyhpFileProcessing:
    Tests that PyHP can load and execute files.
"""

# pylint: disable=missing-function-docstring

from unittest import TestCase
from datetime import datetime
from pathlib import PurePath

try:
    from mocks import MockFileProcessor
except ImportError:
    from .mocks import MockFileProcessor

from src.pyhp.text_processing import remove_initial_indentation, \
    prepare_code_text
from src.pyhp.hypertext_processing import parse_text
from src.pyhp.code_execution import prepare_context, run_parsed_code
from src.pyhp.cookies import NewCookie, DeleteCookie
from src.pyhp.pyhp_interface import Pyhp


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


class TestPyhpPrepareContext(TestCase):
    """Tests that the globals and locals contain the required information."""

    def test_typical_globals(self):
        file_processor = MockFileProcessor()
        pyhp_class = Pyhp(PurePath(), file_processor)
        self.assertIs(prepare_context(pyhp_class, file_processor)[0]['pyhp'],
                      pyhp_class)


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
            run_parsed_code(parse_text(case[0]), pyhp_class, file_processor)
            self.assertEqual(case[1], pyhp_class.get_new_cookies())

    def test_delete_cookies(self):
        # Create a cookie then delete it
        file_processor = MockFileProcessor()
        pyhp_class = Pyhp(PurePath(), file_processor)
        code = '<pyhp>pyhp.set_cookie("foo", value="bar")\n' \
               'pyhp.delete_cookie("foo")</pyhp>'
        run_parsed_code(parse_text(code), pyhp_class, file_processor)
        self.assertEqual({'foo': NewCookie('foo', 'bar')},
                         pyhp_class.get_new_cookies())
        self.assertEqual({'foo': DeleteCookie('foo')},
                         pyhp_class.get_delete_cookies())

        # Start with a cookie then delete it
        pyhp_class = Pyhp(PurePath(), file_processor, cookies={'foo': 'bar'})
        code = '<pyhp>pyhp.delete_cookie("foo")</pyhp>'
        run_parsed_code(parse_text(code), pyhp_class, file_processor)
        self.assertEqual({'foo': DeleteCookie('foo')},
                         pyhp_class.get_delete_cookies())

        # Delete an unexisting cookie
        pyhp_class = Pyhp(PurePath(), file_processor)
        code = '<pyhp>pyhp.delete_cookie("foo")</pyhp>'
        run_parsed_code(parse_text(code), pyhp_class, file_processor)
        # TODO: Should this be empty?
        self.assertEqual({'foo': DeleteCookie('foo')},
                         pyhp_class.get_delete_cookies())

    def test_get_parameters(self):
        cases = [
            ("<pyhp>print(pyhp.get['foo'])</pyhp>", {'foo': 'bar'}, 'bar\n'),
            ("<pyhp>print(pyhp.get['foo'] + ' ' + pyhp.get['baz'])</pyhp>",
             {'foo': 'bar', 'baz': 'qux'}, 'bar qux\n'),
        ]

        for case in cases:
            file_processor = MockFileProcessor()
            pyhp_class = Pyhp(PurePath(), file_processor, get=case[1])
            self.assertEqual(run_parsed_code(parse_text(case[0]), pyhp_class,
                                             file_processor),
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
            self.assertEqual(run_parsed_code(parse_text(case[0]), pyhp_class,
                                             file_processor),
                             case[2])

    def test_include(self):
        pass  # TODO: Finish

    def test_display(self):
        file_processor = MockFileProcessor({
            PurePath('foo.html'): '<p>Hello</p>',
            PurePath('bar.pyhp'): '<pyhp>x=1\nprint(x + 2)</pyhp>',
        })
        pyhp_class = Pyhp(PurePath(), file_processor)

        self.assertEqual(
            run_parsed_code(parse_text('<pyhp>pyhp.display("foo.html")</pyhp>'),
                            pyhp_class, file_processor),
            '<p>Hello</p>'
        )
        self.assertEqual(
            run_parsed_code(parse_text('<pyhp>pyhp.display("bar.pyhp")</pyhp>'),
                            pyhp_class, file_processor),
            '3\n'
        )

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
            self.assertIn(case[1],
                          run_parsed_code(dom, pyhp_class, file_processor))

            # Run without debug
            pyhp_class = Pyhp(PurePath(), file_processor, debug=False)
            with self.assertRaises(RuntimeError):
                run_parsed_code(dom, pyhp_class, file_processor)

    def test_escape(self):
        cases = [
            ('<', '&lt;'),
            ('>', '&gt;'),
            ('&', '&amp;'),
            ('"', '&#34;'),
            ("'", '&#39;'),
            ('<script>', '&lt;script&gt;'),
            ('</script>', '&lt;/script&gt;'),
            ('<pyhp>print("Hello World!")</pyhp>',
             '&lt;pyhp&gt;print(&#34;Hello World!&#34;)&lt;/pyhp&gt;'),
        ]

        for case in cases:
            self.assertEqual(case[1], Pyhp.escape(case[0]))

    def test_redirect(self):
        cases = [
            ('<pyhp>pyhp.redirect("https://www.google.com")</pyhp>',
             ('https://www.google.com', 302)),
            ('<pyhp>pyhp.redirect("http://www.google.com", 301)</pyhp>',
             ('http://www.google.com', 301)),
            ('<pyhp>pyhp.redirect("test", 308)</pyhp>',
             ('test', 308)),
            ('<pyhp></pyhp>', None),
        ]

        for case in cases:
            file_processor = MockFileProcessor()
            pyhp_class = Pyhp(PurePath(), file_processor)
            run_parsed_code(parse_text(case[0]), pyhp_class, file_processor)
            self.assertEqual(pyhp_class.get_redirect_information(), case[1])

    def test_import(self):
        pass  # TODO: Test import


class TestPyhpFileProcessing(TestCase):
    """Tests that PyHP can load and execute files."""

    def test_get_directory(self):
        pass  # TODO: Finish

    def test_get_true_path(self):
        file_contents = {'index.pyhp': '<pyhp>print("Hello")</pyhp>'}
        directories = ['dir', 'foo', 'foo/bar']

        file_processor = MockFileProcessor(
            {PurePath(f): contents for f, contents in file_contents.items()},
            {PurePath(d) for d in directories}
        )

        normal_cases = [
            ('index', 'index.pyhp'),
            ('index.pyhp', 'index.pyhp'),
        ]
        error_cases = [
            ('', ValueError),
            ('index.pyhp.txt', FileNotFoundError),
            ('dir', IsADirectoryError),
            ('foo/bar', IsADirectoryError),
            ('foo/baz', FileNotFoundError),
        ]

        for case in normal_cases:
            self.assertEqual(file_processor.get_true_path(PurePath(case[0])),
                             PurePath(case[1]))

        for case in error_cases:
            with self.assertRaises(case[1]):
                file_processor.get_true_path(PurePath(case[0]))


def create_file_processor_and_run_code(case: str):
    file_processor = MockFileProcessor(case)
    pyhp_class = Pyhp(PurePath(), file_processor)
    return pyhp_class.include('index.pyhp')
