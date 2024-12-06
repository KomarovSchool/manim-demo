import unittest

from utils.route_interpolator import RouteInterpolator


class TestRouteInterpolator(unittest.TestCase):
    def setUp(self):
        # Common route for multiple tests
        self.points = [(0, 0), (3, 4), (6, 0), (9, 4)]
        self.speeds = [5, 10, 5]  # Speeds for each segment
        self.route = RouteInterpolator(self.points, self.speeds)

    def test_start_point(self):
        # Test at 0% of total time
        expected = self.points[0]
        result = self.route(0.0)
        self.assertEqual(result, expected, "At 0%, the coordinate should be the starting point.")

    def test_end_point(self):
        # Test at 100% of total time
        expected = self.points[-1]
        result = self.route(1.0)
        self.assertEqual(result, expected, "At 100%, the coordinate should be the ending point.")

    def test_mid_point(self):
        # Test at 50% of total time
        result = self.route(0.5)
        # Since speeds are different, the midpoint in time may not be the geometric midpoint
        # For this test, we calculate the expected coordinate manually
        total_time = sum(self.route.times)
        elapsed_time = 0.5 * total_time

        # Find expected position manually
        cumulative_time = 0
        for i, segment_time in enumerate(self.route.times):
            if cumulative_time + segment_time >= elapsed_time:
                proportion = (elapsed_time - cumulative_time) / segment_time
                x_start, y_start = self.points[i]
                x_end, y_end = self.points[i + 1]
                expected_x = x_start + proportion * (x_end - x_start)
                expected_y = y_start + proportion * (y_end - y_start)
                expected = (expected_x, expected_y)
                break
            cumulative_time += segment_time

        self.assertAlmostEqual(result[0], expected[0], places=6, msg="X coordinate mismatch at 50% time.")
        self.assertAlmostEqual(result[1], expected[1], places=6, msg="Y coordinate mismatch at 50% time.")

    def test_before_start(self):
        # Test with X less than 0
        result = self.route(-0.5)
        expected = self.points[0]
        self.assertEqual(result, expected, "X less than 0 should return the starting point.")

    def test_after_end(self):
        # Test with X greater than 1
        result = self.route(1.5)
        expected = self.points[-1]
        self.assertEqual(result, expected, "X greater than 1 should return the ending point.")

    def test_exact_segment_point(self):
        # Test at exact cumulative time of the first segment
        first_segment_time = self.route.times[0]
        elapsed_time = first_segment_time / self.route.total_time
        result = self.route(elapsed_time)
        expected = self.points[1]
        self.assertEqual(result, expected, "At cumulative time of first segment, should be at the second point.")

    def test_non_uniform_speeds(self):
        # Test with varying speeds and positions
        points = [(0, 0), (10, 0), (10, 10), (0, 10)]
        speeds = [5, 10, 5]
        route = RouteInterpolator(points, speeds)

        # Test at 25% of total time
        result = route(0.25)
        # Manually calculate expected position
        total_time = sum(route.times)
        elapsed_time = 0.25 * total_time

        cumulative_time = 0
        for i, segment_time in enumerate(route.times):
            if cumulative_time + segment_time >= elapsed_time:
                proportion = (elapsed_time - cumulative_time) / segment_time
                x_start, y_start = points[i]
                x_end, y_end = points[i + 1]
                expected_x = x_start + proportion * (x_end - x_start)
                expected_y = y_start + proportion * (y_end - y_start)
                expected = (expected_x, expected_y)
                break
            cumulative_time += segment_time

        self.assertAlmostEqual(result[0], expected[0], places=6, msg="X coordinate mismatch at 25% time.")
        self.assertAlmostEqual(result[1], expected[1], places=6, msg="Y coordinate mismatch at 25% time.")

    def test_single_segment(self):
        # Test with a single segment
        points = [(1, 1), (4, 5)]
        speeds = [3]
        route = RouteInterpolator(points, speeds)
        result = route(0.5)
        expected_x = (1 + 4) / 2
        expected_y = (1 + 5) / 2
        expected = (expected_x, expected_y)
        self.assertAlmostEqual(result[0], expected[0], places=6, msg="X coordinate mismatch for single segment at 50% time.")
        self.assertAlmostEqual(result[1], expected[1], places=6, msg="Y coordinate mismatch for single segment at 50% time.")

    def test_zero_length_segment(self):
        # Test with zero-length segment (consecutive identical points)
        points = [(0, 0), (0, 0), (5, 5)]
        speeds = [1, 1]
        route = RouteInterpolator(points, speeds)
        result = route(0.25)
        expected = (1.25, 1.25)
        self.assertEqual(result, expected, "Zero-length segment should not affect position at early times.")

    def test_no_movement(self):
        # Test with no movement (all points are the same)
        points = [(2, 2), (2, 2), (2, 2)]
        speeds = [1, 1]
        route = RouteInterpolator(points, speeds)
        result = route(0.5)
        expected = (2, 2)
        self.assertEqual(result, expected, "No movement should always return the same point.")


if __name__ == '__main__':
    unittest.main()
