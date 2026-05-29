"""
Tests for modules/jd_matcher.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from modules.jd_matcher import (
    extract_skills_from_text, extract_jd_keywords,
    compute_cosine_similarity, match_keywords, match_resume_to_jd
)


SAMPLE_RESUME_PARSED = {
    'raw_text': """Priya Sharma. Data Analyst skilled in Python, SQL, Excel, Tableau.
    Analyzed 50,000 customer records. Built dashboards. Machine learning experience.
    B.Tech Computer Science.""",
    'contact': {'name': 'Priya Sharma', 'email': 'priya@email.com'},
    'sections': {},
    'keywords': ['python', 'sql', 'excel', 'tableau']
}

SAMPLE_JD = """
Data Analyst position. Required: Python, SQL, Excel, Tableau, Power BI.
Experience with data visualization and statistical analysis.
Must have 2+ years experience in data analysis and business intelligence.
MBA or B.Tech preferred.
"""


class TestSkillExtraction(unittest.TestCase):

    def test_skills_found(self):
        text = 'I know Python, SQL, Excel, and Tableau for data analysis'
        skills = extract_skills_from_text(text)
        self.assertIn('python', skills)
        self.assertIn('sql', skills)
        self.assertIn('excel', skills)
        self.assertIn('tableau', skills)

    def test_empty_text(self):
        skills = extract_skills_from_text('')
        self.assertEqual(skills, [])

    def test_no_skills(self):
        text = 'the quick brown fox jumped over the lazy dog'
        skills = extract_skills_from_text(text)
        self.assertEqual(skills, [])


class TestKeywordExtraction(unittest.TestCase):

    def test_keywords_returned(self):
        keywords = extract_jd_keywords(SAMPLE_JD, top_n=20)
        self.assertIsInstance(keywords, list)
        self.assertGreater(len(keywords), 0)

    def test_relevant_keywords(self):
        keywords = extract_jd_keywords(SAMPLE_JD, top_n=30)
        keywords_lower = [k.lower() for k in keywords]
        # At least some relevant terms should appear
        self.assertTrue(any('data' in k or 'analyst' in k or 'python' in k for k in keywords_lower))


class TestCosineSimilarity(unittest.TestCase):

    def test_identical_texts(self):
        text = 'Python SQL Excel data analysis'
        sim = compute_cosine_similarity(text, text)
        self.assertAlmostEqual(sim, 1.0, places=2)

    def test_unrelated_texts(self):
        text1 = 'Python SQL Excel database'
        text2 = 'cooking recipe kitchen food restaurant'
        sim = compute_cosine_similarity(text1, text2)
        self.assertLess(sim, 0.3)

    def test_similar_texts_higher_than_different(self):
        text1 = 'Python data analysis SQL Excel Tableau'
        text2 = 'Python data analyst SQL Excel Power BI'
        text3 = 'cooking baking kitchen recipe food'
        sim_similar = compute_cosine_similarity(text1, text2)
        sim_different = compute_cosine_similarity(text1, text3)
        self.assertGreater(sim_similar, sim_different)

    def test_empty_texts(self):
        sim = compute_cosine_similarity('', 'some text')
        self.assertEqual(sim, 0.0)


class TestKeywordMatching(unittest.TestCase):

    def test_matched_keywords(self):
        resume = 'Python SQL Excel Tableau machine learning'
        jd_keywords = ['python', 'sql', 'excel', 'power bi', 'machine learning']
        matched, missing = match_keywords(resume, jd_keywords)
        self.assertIn('python', matched)
        self.assertIn('sql', matched)
        self.assertIn('machine learning', matched)
        self.assertIn('power bi', missing)

    def test_no_matches(self):
        resume = 'cooking baking food'
        jd_keywords = ['python', 'sql', 'excel']
        matched, missing = match_keywords(resume, jd_keywords)
        self.assertEqual(matched, [])
        self.assertEqual(len(missing), 3)


class TestFullJDMatching(unittest.TestCase):

    def test_match_structure(self):
        result = match_resume_to_jd(SAMPLE_RESUME_PARSED, SAMPLE_JD)
        self.assertIn('fit_score', result)
        self.assertIn('matched_keywords', result)
        self.assertIn('missing_keywords', result)
        self.assertIn('matched_skills', result)
        self.assertIn('missing_skills', result)
        self.assertIn('suggestions', result)

    def test_fit_score_range(self):
        result = match_resume_to_jd(SAMPLE_RESUME_PARSED, SAMPLE_JD)
        self.assertGreaterEqual(result['fit_score'], 0)
        self.assertLessEqual(result['fit_score'], 100)

    def test_good_match_higher_score(self):
        good_resume = {
            'raw_text': 'Python SQL Excel Tableau Power BI data analysis data visualization statistical analysis business intelligence',
            'contact': {'name': 'Test'}
        }
        poor_resume = {
            'raw_text': 'cooking baking food kitchen restaurant',
            'contact': {'name': 'Test'}
        }
        good_result = match_resume_to_jd(good_resume, SAMPLE_JD)
        poor_result = match_resume_to_jd(poor_resume, SAMPLE_JD)
        self.assertGreater(good_result['fit_score'], poor_result['fit_score'])

    def test_suggestions_honest(self):
        result = match_resume_to_jd(SAMPLE_RESUME_PARSED, SAMPLE_JD)
        suggestions_text = ' '.join(result['suggestions']).lower()
        # Should mention verification, not add fake skills
        self.assertTrue(
            'verify' in suggestions_text or 'learn' in suggestions_text or 'claiming' in suggestions_text
        )


if __name__ == '__main__':
    unittest.main()
