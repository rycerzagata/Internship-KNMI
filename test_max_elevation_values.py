import unittest
import numpy as np
from max_elevation_values import interpolate


class TestMaxElevationValues(unittest.TestCase):

    def setUp(self) -> None:
        self.height_map = np.array([[1, 1, 3],
                                    [1, 1, 3],
                                    [2, 2, 10]], dtype='int')

    def test_interpolate_exact(self):
        self.assertEqual(1, interpolate(height_map=self.height_map, point=(0, 0)))

    def test_interpolate_between_ones(self):
        self.assertEqual(1, interpolate(height_map=self.height_map, point=(0.5, 0.5)))

    def test_interpolate_between_ones_and_twos(self):
        self.assertEqual(1.5, interpolate(height_map=self.height_map, point=(0, 1.5)))

    def test_interpolate_out_of_bounds(self):
        with self.assertRaises(expected_exception=AssertionError):
            interpolate(height_map=self.height_map, point=(-1, -1))


if __name__ == '__main__':
    unittest.main()
