import unittest
import pandas as pd
from df_operations import check_missing_records, check_missing_records_points

class TestDfOperations(unittest.TestCase):

    def setUp(self):
        # Sample data for lines
        self.df1_lines = pd.DataFrame({
            'ROADNAME': ['Road1', 'Road2', 'Road1', 'Road3'],
            'MeasureFromKM': [0.0, 0.0, 1.0, 0.0],
            'MeasureToKM': [1.0, 2.0, 2.0, 1.0]
        })

        self.df2_lines = pd.DataFrame({
            'ROADNAME': ['Road1', 'Road2', 'Road1', 'Road3'],
            'MeasureFromKM': [0.0, 0.0, 1.5, 0.0],
            'MeasureToKM': [1.5, 2.5, 2.5, 1.0]
        })

        # Sample data for points
        self.df1_points = pd.DataFrame({
            'ROADNAME': ['Road1', 'Road2', 'Road1', 'Road3'],
            'Measure': [0.0, 0.0, 1.0, 0.0]
        })

        self.df2_points = pd.DataFrame({
            'ROADNAME': ['Road1', 'Road2', 'Road1', 'Road3'],
            'Measure': [0.0, 0.0, 1.5, 0.0]
        })

        self.id_columns_lines = ['ROADNAME', 'MeasureFromKM', 'MeasureToKM']
        self.id_columns_points = ['ROADNAME', 'Measure']

    def test_check_missing_records(self):
        result = check_missing_records(self.df1_lines, self.df2_lines, self.id_columns_lines)
        expected_result = (
            "\n\nSegments removed from database:\n"
            "Road1-1.00000-2.00000 segments: 1\n"
            "\n\nSegments added to database:\n"
            "Road1-1.50000-2.50000 segments: 1\n"
        )
        self.assertIn("Segments removed from database:", result)
        self.assertIn("Segments added to database:", result)

    def test_check_missing_records_points(self):
        result = check_missing_records_points(self.df1_points, self.df2_points, self.id_columns_points)
        expected_result = (
            "\n\nPoints removed from database:\n"
            "Road1 1.00000-1.00000 points: 1\n"
            "\n\nPoints added to database:\n"
            "Road1 1.50000-1.50000 points: 1\n"
        )
        self.assertIn("Points removed from database:", result)
        self.assertIn("Points added to database:", result)

if __name__ == '__main__':
    unittest.main()
