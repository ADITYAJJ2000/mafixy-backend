import unittest
from unittest.mock import patch, MagicMock
import numpy as np
from main import (
    calculate_symmetry,
    calculate_jawline,
    calculate_facial_ratio,
    analyze_image
)

class TestFaceAnalysis(unittest.TestCase):
    def setUp(self):
        # Create mock landmarks for testing
        self.mock_landmarks = [
            [100, 100],  # Left eye
            [200, 100],  # Right eye
            [150, 200],  # Nose
            [100, 300],  # Left mouth
            [200, 300],  # Right mouth
            # Add more landmarks as needed
        ]
        
        # Create mock image
        self.mock_image = np.zeros((400, 400, 3), dtype=np.uint8)

    def test_calculate_symmetry(self):
        """Test symmetry calculation with perfect and imperfect symmetry."""
        # Perfect symmetry
        perfect_landmarks = [
            [100, 100],  # Left point
            [300, 100],  # Right point
            [100, 200],  # Left point
            [300, 200],  # Right point
            # Add more points
        ]
        
        symmetry_score = calculate_symmetry(perfect_landmarks)
        self.assertAlmostEqual(symmetry_score, 100.0, delta=1.0)

        # Imperfect symmetry
        imperfect_landmarks = [
            [100, 100],  # Left point
            [300, 120],  # Right point (slightly offset)
            [100, 200],  # Left point
            [300, 220],  # Right point (slightly offset)
        ]
        
        symmetry_score = calculate_symmetry(imperfect_landmarks)
        self.assertLess(symmetry_score, 100.0)
        self.assertGreater(symmetry_score, 0.0)

    def test_calculate_jawline(self):
        """Test jawline score calculation."""
        # Straight jawline
        straight_jawline = [
            [100, 300],  # Left
            [150, 300],  # Center
            [200, 300],  # Right
        ]
        
        jawline_score = calculate_jawline(straight_jawline)
        self.assertAlmostEqual(jawline_score, 100.0, delta=1.0)

        # Uneven jawline
        uneven_jawline = [
            [100, 300],  # Left
            [150, 310],  # Center (slightly up)
            [200, 300],  # Right
        ]
        
        jawline_score = calculate_jawline(uneven_jawline)
        self.assertLess(jawline_score, 100.0)
        self.assertGreater(jawline_score, 0.0)

    def test_calculate_facial_ratio(self):
        """Test facial ratio calculation."""
        # Ideal golden ratio
        golden_ratio_landmarks = {
            'top': [150, 100],  # Forehead
            'bottom': [150, 300],  # Chin
            'left': [100, 200],  # Left cheek
            'right': [200, 200],  # Right cheek
        }
        
        ratio_score = calculate_facial_ratio(golden_ratio_landmarks)
        self.assertAlmostEqual(ratio_score, 100.0, delta=1.0)

        # Non-ideal ratio
        non_ideal_landmarks = {
            'top': [150, 100],  # Forehead
            'bottom': [150, 350],  # Chin (longer face)
            'left': [100, 200],  # Left cheek
            'right': [200, 200],  # Right cheek
        }
        
        ratio_score = calculate_facial_ratio(non_ideal_landmarks)
        self.assertLess(ratio_score, 100.0)
        self.assertGreater(ratio_score, 0.0)

    @patch('main.face_mesh.process')
    def test_analyze_image(self, mock_process):
        """Test complete image analysis pipeline."""
        # Mock MediaPipe results
        mock_landmarks = MagicMock()
        mock_landmarks.landmark = [
            type('Landmark', (), {'x': x/400, 'y': y/400})
            for x, y in self.mock_landmarks
        ]
        
        mock_results = MagicMock()
        mock_results.multi_face_landmarks = [mock_landmarks]
        mock_process.return_value = mock_results

        # Run analysis
        result = analyze_image(self.mock_image)
        
        # Verify results
        self.assertTrue(result['success'])
        self.assertIn('scores', result)
        self.assertIn('symmetry', result['scores'])
        self.assertIn('jawline', result['scores'])
        self.assertIn('facial_ratio', result['scores'])
        self.assertIn('improvement_tips', result)

if __name__ == '__main__':
    unittest.main()
