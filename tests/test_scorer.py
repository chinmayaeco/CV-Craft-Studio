"""
Tests for modules/scorer.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from modules.scorer import (
    score_contact_info, score_skills, score_experience,
    score_action_verbs, score_quantified, detect_red_flags, score_resume
)
from modules.parser import parse_resume


SAMPLE_PARSED = {
    'raw_text': """John Doe\njohn@example.com | +91-9876543210 | linkedin.com/in/johndoe\n
PROFESSIONAL SUMMARY\nData analyst with 3 years of experience. Analyzed 2M+ records and reduced costs by 20%.

SKILLS\nPython, SQL, Excel, Tableau, Power BI, Machine Learning, Data Visualization

EXPERIENCE\nData Analyst | ABC Corp | 2021-2024\n- Analyzed customer data to identify trends, increasing revenue by 15%\n- Developed automated dashboards reducing reporting time by 40%

EDUCATION\nB.Tech Computer Science | 2021\n""",
    'contact': {
        'name': 'John Doe',
        'email': 'john@example.com',
        'phone': '+91-9876543210',
        'linkedin': 'linkedin.com/in/johndoe',
        'github': ''
    },
    'sections': {
        'summary': 'Data analyst with 3 years of experience. Analyzed 2M+ records and reduced costs by 20%.',
        'skills': 'Python, SQL, Excel, Tableau, Power BI, Machine Learning, Data Visualization',
        'experience': 'Data Analyst | ABC Corp | 2021-2024\n- Analyzed customer data to identify trends, increasing revenue by 15%',
        'education': 'B.Tech Computer Science | 2021'
    },
    'keywords': ['python', 'sql', 'excel'],
    'word_count': 80,
    'line_count': 10,
    'char_count': 500,
    'filename': 'test.txt'
}


class TestContactScoring(unittest.TestCase):

    def test_full_contact(self):
        score, strengths, issues = score_contact_info(SAMPLE_PARSED)
        self.assertGreater(score, 7)
        self.assertIsInstance(strengths, list)

    def test_missing_email(self):
        parsed = dict(SAMPLE_PARSED)
        parsed['contact'] = {'name': 'John', 'email': '', 'phone': '1234567890', 'linkedin': '', 'github': ''}
        score, _, issues = score_contact_info(parsed)
        self.assertTrue(any('email' in i.lower() for i in issues))


class TestSkillsScoring(unittest.TestCase):

    def test_skills_present(self):
        score, strengths, issues = score_skills(SAMPLE_PARSED)
        self.assertGreater(score, 5)

    def test_no_skills(self):
        parsed = dict(SAMPLE_PARSED)
        parsed['sections'] = {}
        score, _, issues = score_skills(parsed)
        self.assertEqual(score, 0)
        self.assertTrue(len(issues) > 0)


class TestActionVerbScoring(unittest.TestCase):

    def test_action_verbs_found(self):
        score, strengths, issues = score_action_verbs(SAMPLE_PARSED)
        self.assertGreater(score, 0)

    def test_no_action_verbs(self):
        parsed = dict(SAMPLE_PARSED)
        parsed['raw_text'] = 'John Doe. Worked on things. Helped with stuff.'
        score, _, issues = score_action_verbs(parsed)
        self.assertLessEqual(score, 5)


class TestQuantifiedScoring(unittest.TestCase):

    def test_quantified_found(self):
        score, strengths, issues = score_quantified(SAMPLE_PARSED)
        self.assertGreater(score, 0)

    def test_no_metrics(self):
        parsed = dict(SAMPLE_PARSED)
        parsed['raw_text'] = 'Worked on projects. Helped the team. Did analysis.'
        score, _, issues = score_quantified(parsed)
        self.assertEqual(score, 0)


class TestRedFlags(unittest.TestCase):

    def test_flags_returned(self):
        parsed_empty = {
            'raw_text': 'Some text here',
            'contact': {'name': '', 'email': '', 'phone': '', 'linkedin': '', 'github': ''},
            'sections': {},
            'word_count': 3
        }
        flags = detect_red_flags(parsed_empty)
        self.assertIsInstance(flags, list)
        self.assertGreater(len(flags), 0)
        severities = [f['severity'] for f in flags]
        self.assertIn('critical', severities)

    def test_no_flags_good_resume(self):
        flags = detect_red_flags(SAMPLE_PARSED)
        critical = [f for f in flags if f['severity'] == 'critical']
        self.assertEqual(len(critical), 0)


class TestFullScoring(unittest.TestCase):

    def test_score_range(self):
        result = score_resume(SAMPLE_PARSED)
        self.assertGreaterEqual(result['total_score'], 0)
        self.assertLessEqual(result['total_score'], 100)

    def test_result_structure(self):
        result = score_resume(SAMPLE_PARSED)
        self.assertIn('total_score', result)
        self.assertIn('grade', result)
        self.assertIn('sections', result)
        self.assertIn('strengths', result)
        self.assertIn('critical_fixes', result)
        self.assertIn('red_flags', result)

    def test_empty_resume_low_score(self):
        empty = {
            'raw_text': '',
            'contact': {'name': '', 'email': '', 'phone': '', 'linkedin': '', 'github': ''},
            'sections': {},
            'word_count': 0,
            'line_count': 0,
            'char_count': 0,
            'filename': 'empty.txt'
        }
        result = score_resume(empty)
        self.assertLess(result['total_score'], 30)


if __name__ == '__main__':
    unittest.main()
