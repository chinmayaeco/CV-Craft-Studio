"""
Tests for modules/parser.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from modules.parser import (
    parse_txt, extract_email, extract_phone, extract_linkedin,
    extract_github, extract_name, extract_contact_info, extract_sections,
    extract_keywords, parse_resume
)


class TestContactExtraction(unittest.TestCase):

    def test_extract_email(self):
        self.assertEqual(extract_email('Contact: john@example.com'), 'john@example.com')
        self.assertEqual(extract_email('no email here'), '')
        self.assertEqual(extract_email('multi@domain.co.uk'), 'multi@domain.co.uk')

    def test_extract_phone(self):
        result = extract_phone('+91-9876543210')
        self.assertTrue(len(result) > 0)
        result2 = extract_phone('call me on 9876543210')
        self.assertTrue(len(result2) > 0)

    def test_extract_linkedin(self):
        result = extract_linkedin('Visit linkedin.com/in/johndoe')
        self.assertIn('johndoe', result)

    def test_extract_github(self):
        result = extract_github('github.com/janedoe')
        self.assertIn('janedoe', result)

    def test_extract_name(self):
        text = 'John Smith\njohn@email.com\n+91-9999999999'
        name = extract_name(text)
        self.assertIn('John', name)

    def test_extract_contact_info(self):
        text = 'Priya Sharma\npriya@email.com\n+91-9876543210\nlinkedin.com/in/priyasharma'
        info = extract_contact_info(text)
        self.assertIn('@', info['email'])
        self.assertIsInstance(info, dict)


class TestSectionExtraction(unittest.TestCase):

    def test_section_detection(self):
        text = """SKILLS\nPython, SQL, Excel\nEDUCATION\nB.Tech 2024"""
        sections = extract_sections(text)
        self.assertIn('skills', sections)
        self.assertIn('education', sections)

    def test_section_content(self):
        text = """SKILLS\nPython SQL Excel"""
        sections = extract_sections(text)
        self.assertIn('Python', sections.get('skills', ''))


class TestKeywordExtraction(unittest.TestCase):

    def test_keywords_returned(self):
        text = 'Analyzed sales data using Python and SQL to identify trends'
        keywords = extract_keywords(text, top_n=10)
        self.assertIsInstance(keywords, list)
        self.assertGreater(len(keywords), 0)

    def test_stopwords_excluded(self):
        text = 'the and or but is are this that'
        keywords = extract_keywords(text, top_n=10)
        for kw in keywords:
            self.assertNotIn(kw.lower(), ['the', 'and', 'or', 'but', 'is'])


class TestParseResume(unittest.TestCase):

    def test_parse_txt(self):
        sample = b"""John Doe\njohn@email.com\n\nSKILLS\nPython SQL"""
        result = parse_resume(sample, 'test.txt')
        self.assertIn('contact', result)
        self.assertIn('sections', result)
        self.assertIn('keywords', result)
        self.assertGreater(result['word_count'], 0)

    def test_empty_input(self):
        result = parse_resume(b'', 'empty.txt')
        self.assertEqual(result['word_count'], 0)


if __name__ == '__main__':
    unittest.main()
