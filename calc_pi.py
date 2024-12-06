import math
import bisect

from manim import *
from manim.utils.color.X11 import CYAN1, MAGENTA3


AXIS_MARGINS = (20, 20)
MAIN_AREA_DIMENSIONS = (100, 60)
MAIN_AREA_MARGIN = 10
COORDS_STEP = 10


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


class RunnerAnimation(Animation):
    def __init__(
        self,
        mobject,
        route: list[tuple[float, float]],
        speeds: list[float],
        speed_factor: float = 1,
        cs: CoordinateSystem = None,
        **kwargs
    ):
        super().__init__(mobject, **kwargs)
        self.ri = RouteInterpolator(route, speeds)
        self.speed_factor = speed_factor
        self.set_run_time(self.ri.total_time / self.speed_factor)
        self.cs = cs

    def interpolate_mobject(self, alpha):
        # Custom behavior for the animation
        self.mobject.move_to(self.cs.c2p(*self.ri(alpha)))


class OGLIntroScene(Scene):
    def construct(self):
        left_x = -AXIS_MARGINS[0]
        right_x = MAIN_AREA_DIMENSIONS[0] + 2 * MAIN_AREA_MARGIN
        ax = NumberPlane(
            x_range=[left_x, right_x, COORDS_STEP],
            y_range=[
                -AXIS_MARGINS[1],
                MAIN_AREA_DIMENSIONS[1] + 2 * MAIN_AREA_MARGIN,
                COORDS_STEP,
            ],
            x_length=14.2,
            y_length=8,
            y_axis_config={
                "stroke_color": WHITE,
                "include_ticks": True,
                "label_direction": UL,  # Offset ticks to the left
            },
            faded_line_style={"stroke_width": 0.5},
        ).add_coordinates()
        # self.add(ax)

        top_y = 50
        bottom_y = 30

        ax.get_x_unit_size()
        top_line, bottom_line = [
            Line(ax.c2p(left_x, y), ax.c2p(right_x, y, 0), color=YELLOW)
            for y in (top_y, bottom_y)
        ]
        water = Rectangle(
            width=15,
            height=ax.get_y_unit_size() * 20,
            color=BLUE,
            fill_opacity=0.2,
            stroke_opacity=0,
        ).move_to(ax.c2p((left_x + right_x) / 2, (top_y + bottom_y) / 2))

        start_coords = 10, 70
        end_coords = 110, 10

        start = Dot(color=GREEN).move_to(ax.c2p(*start_coords))
        finish = Dot(color=RED).move_to(ax.c2p(*end_coords))

        start_label = Text("Start").scale(0.5).next_to(start, UR)
        finish_label = Text("Finish").scale(0.5).next_to(finish, DL)

        self.play(Create(ax))
        self.play(Create(top_line), Create(bottom_line), FadeIn(water))
        self.play(
            Create(start), Create(finish), Create(start_label), Create(finish_label)
        )
        self.wait()

        routes = [
            (
                [start_coords, (10, 50), (10, 30), (10, 10), end_coords],
                [4, 2, 4, 4],
                PINK,
            ),
            ([start_coords, (110, 50), (110, 30), end_coords], [4, 2, 4], YELLOW),
            ([start_coords, (60, 50), (60, 30), end_coords], [4, 2, 4], GREEN),
            (
                [start_coords, (43.333, 50), (76.6666, 30), end_coords],
                [4, 2, 4],
                MAGENTA3,
            ),
            (
                [start_coords, (43.333, 50), (76.6666, 30), end_coords],
                [4, 2, 4],
                BLUE,
            ),
        ]

        players = [Dot(ax.c2p(*start_coords), color=color) for _, _, color in routes]
        self.add(*players)
        animations = [
            RunnerAnimation(runner, route_points, speeds, 3, ax)
            for runner, (route_points, speeds, _) in zip(players, routes)
        ]
        traces = [
            TracedPath(p.get_center, stroke_width=4, stroke_color=p.get_color())
            for p in players
        ]
        self.add(*traces)
        self.play(AnimationGroup(*animations))
        self.remove(*players, *traces)

        self.wait()
        self.next_section()

        dot_a = Dot(ax.c2p(10, 50), color=RED)
        dot_b = Dot(ax.c2p(110, 30), color=RED)

        start2a = always_redraw(
            lambda: Line(ax.c2p(*start_coords), dot_a.get_center(), color=RED)
        )
        a2b = always_redraw(
            lambda: Line(dot_a.get_center(), dot_b.get_center(), color=RED)
        )
        b2finish = always_redraw(
            lambda: Line(dot_b.get_center(), ax.c2p(*end_coords), color=RED)
        )

        self.play(*(Create(o) for o in (dot_a, dot_b, start2a, a2b, b2finish)))

        positions = [[60, 70], [40, 70], [40, 50], [60, 60], [10, 110], [20, 100]]

        for x_a, x_b in positions:
            self.play(
                dot_a.animate.move_to(
                    ax.c2p(x_a, 50),
                ),
                dot_b.animate.move_to(ax.c2p(x_b, 30)),
            )
            self.wait()
