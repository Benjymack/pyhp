"""
Tests the UglySoup HTML/PyHP parser.
"""

# pylint: disable=missing-function-docstring

from unittest import TestCase

from src.pyhp.hypertext_processing import UglySoup, Section


class TestUglySoup(TestCase):
    """Test the UglySoup HTML/PyHP parser."""
    def test_no_code(self):
        cases = [
            ('', []),
            ('<p>hello</p>', [Section(False, '<p>hello</p>')]),
            ('<p>hello</p><p>world</p>', [Section(False, '<p>hello</p><p>world</p>')]),
            ('\n<p>hello</p>\n<p>world</p>\n', [Section(False, '\n<p>hello</p>\n<p>world</p>\n')]),
        ]

        for html, expected_sections in cases:
            with self.subTest(html=html):
                self.assertEqual(UglySoup(html).sections, expected_sections)

    def test_all_code(self):
        cases = [
            ('<pyhp>print("hello")</pyhp>', [Section(True, 'print("hello")')]),
            ('<pyhp>print("hello")</pyhp><pyhp>print("world")</pyhp>',
             [Section(True, 'print("hello")'), Section(True, 'print("world")')]),
        ]

        for html, expected_sections in cases:
            with self.subTest(html=html):
                self.assertEqual(UglySoup(html).sections, expected_sections)

    def test_mixed(self):
        cases = [
            ('<p>hello</p><pyhp>print("world")</pyhp>',
             [Section(False, '<p>hello</p>'), Section(True, 'print("world")')]),
            ('<pyhp>print("hello")</pyhp><p>world</p>',
             [Section(True, 'print("hello")'), Section(False, '<p>world</p>')]),
        ]

        for html, expected_sections in cases:
            with self.subTest(html=html):
                self.assertEqual(UglySoup(html).sections, expected_sections)
