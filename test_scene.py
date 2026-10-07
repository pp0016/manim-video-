from manim import *
class Test(Scene):
    def construct(self):
        for i in range(10):
            self.play(Write(Text(str(i))))
