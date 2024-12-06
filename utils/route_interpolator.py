import math
import bisect


class RouteInterpolator:
    def __init__(self, points, speeds):

        self.points = points
        self.speeds = speeds
        self.distances = []
        self.times = []
        self.cumulative_times = [0]

        # Calculate distances and times for each segment
        for i in range(len(points) - 1):
            dx = points[i + 1][0] - points[i][0]
            dy = points[i + 1][1] - points[i][1]
            distance = math.hypot(dx, dy)
            time = distance / speeds[i]
            self.distances.append(distance)
            self.times.append(time)
            self.cumulative_times.append(self.cumulative_times[-1] + time)

        # Total time of the journey
        self.total_time = self.cumulative_times[-1]

    def __call__(self, t):
        # Clamp X to [0, 1]
        t = max(0.0, min(1.0, t))

        # Determine elapsed time
        elapsed_time = t * self.total_time

        # Find the segment where the elapsed time falls
        segment_index = bisect.bisect_right(self.cumulative_times, elapsed_time) - 1

        # Handle edge cases
        if segment_index >= len(self.points) - 1:
            result = (*self.points[-1], 0)
            return result
        if elapsed_time == self.cumulative_times[segment_index]:
            result = (*self.points[segment_index], 0)
            return result

        # Calculate proportion along the segment
        segment_time = self.times[segment_index]
        time_into_segment = elapsed_time - self.cumulative_times[segment_index]
        proportion = time_into_segment / segment_time

        # Compute coordinate
        x_start, y_start = self.points[segment_index]
        x_end, y_end = self.points[segment_index + 1]
        x = x_start + proportion * (x_end - x_start)
        y = y_start + proportion * (y_end - y_start)
        result = (x, y, 0)
        return result
