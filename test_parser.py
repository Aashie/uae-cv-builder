import unittest
from utils.job_parser import parse_job_description

class TestJobParser(unittest.TestCase):
    
    def test_parse_job_description(self):
        sample_text = "We are looking for a Senior Data Analyst. Requires Bachelor's degree. Skills: Microsoft Excel, documentation. Traits: Leadership, teamwork."
        
        result = parse_job_description(sample_text)
        
        # Verify the structure using dot notation (Objects)
        self.assertEqual(result.job_title, "Senior Data Analyst")
        self.assertIn("Microsoft Excel", result.required_skills)
        self.assertIn("Leadership", result.soft_skills)
        self.assertEqual(result.experience_level, "Senior")
        self.assertEqual(result.education, "Bachelor's Degree")
        self.assertEqual(result.certifications, []) # None in the sample text
        self.assertIn("Senior Data Analyst", result.keywords) # Check if title is in keywords
        
        print("\n✅ Test Passed: All Intelligence Layer components are functional.")

if __name__ == '__main__':
    unittest.main()