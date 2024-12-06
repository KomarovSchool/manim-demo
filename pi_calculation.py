from manim import *
import random


random.seed(42)


class PICalculation(Scene):
    def construct(self):
        t = Title(r"$ \text{Calculating } \pi \text{ using Monte-Carlo method} $")
        self.play(Write(t))
        self.wait(3)
        self.next_section()
        self.clear()
        ax = (
            NumberPlane(
                x_range=(-3.5, 3.5, 0.5),
                y_range=(-1.25, 1.25, 0.5),
            )
            .scale(3)
            .add_coordinates()
        )

        circle = Circle(radius=1 * ax.get_x_unit_size(), color=RED)
        self.play(Create(ax))
        self.play(Create(circle))

        self.wait(1)

        square = Square(2 * ax.get_x_unit_size(), color=GREEN).move_to(ax.c2p(0, 0))
        self.play(Create(square))
        self.wait(1)

        points = [
            (random.random() * 2 - 1, random.random() * 2 - 1) for _ in range(1000)
        ]

        def get_color(x, y):
            if x**2 + y**2 > 1:
                return GREEN
            return RED

        dots = [
            Dot(ax.c2p(x, y), radius=0.03, color=get_color(x, y)) for x, y in points
        ]
        self.play(Create(VGroup(*dots), lag_ratio=0.1))
        self.wait(3)
        total_red = sum(1 for x, y in points if x**2 + y**2 <= 1)
        results = Text(
            f"Red = {total_red}\nTotal = 1000", t2c={"Red": RED}, font_size=24
        ).to_edge(UP + RIGHT)
        background_rect = BackgroundRectangle(results, fill_opacity=0.75, color=BLACK)

        # Group them together so the rectangle stays behind the text
        text_with_background = VGroup(background_rect, results)
        self.play(Create(text_with_background))
        self.wait(3)

        self.clear()
        self.next_section()
        texts = [
            r"$ \text{Area of the circle } = \pi r^2 = \pi $",
            r"$ \text{Area of the square } = 2 \times 2 = 4 $",
            r"$ \text{Ratio of areas: } \frac {\pi}{4} $",
            r"$ \text{Proportion inside the circle } \approx \frac{N_{Red}}{N} \approx \frac{\pi}{4} $",
            r"$ \pi \approx 4 \cdot \frac{N_{\text{Red}}}{N} = 4 \times \frac{795}{1000} =  3.18 $",
        ]
        tex_objects = [Tex(t) for t in texts]
        vg = VGroup(*tex_objects).to_edge(UP)
        vg.arrange(DOWN, buff=0.5)
        ag = AnimationGroup([Create(t) for t in tex_objects], lag_ratio=1.5)
        self.play(ag)
        self.wait(3)
