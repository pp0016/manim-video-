from manim import *

class Var1Kinetic(Scene):
    def construct(self):
        self.camera.background_color = "#0A0A0A" # Deep cinematic black
        
        # ==========================================
        # ANIMATIONS 0-1 (0:00 - 0:03)
        # ==========================================
        # Professional Eye Vector Graphic
        eye_top = ArcBetweenPoints(LEFT*1.5, RIGHT*1.5, angle=PI/2, color=WHITE, stroke_width=8)
        eye_bottom = ArcBetweenPoints(RIGHT*1.5, LEFT*1.5, angle=PI/2, color=WHITE, stroke_width=8)
        iris = Circle(radius=0.5, color="#00D4FF", fill_opacity=1).move_to(ORIGIN)
        pupil = Circle(radius=0.2, color=BLACK, fill_opacity=1).move_to(ORIGIN)
        eye = VGroup(eye_top, eye_bottom, iris, pupil).scale(0.5).shift(UP*1.5)
        
        text1 = Text("KABHI NOTICE KIYA?", font_size=55, weight=BOLD, color=WHITE).shift(DOWN*0.5)
        self.play(FadeIn(eye, scale=0.5), Write(text1), run_time=2)
        
        # ==========================================
        # ANIMATIONS 2-3 (0:03 - 0:06)
        # ==========================================
        text2 = Text("BINA FORCE KIYE", font_size=60, color="#FFB800", weight=BOLD)
        text3 = Text("TRUST & RESPECT", font_size=75, color="#00D4FF", weight=BOLD).shift(DOWN*1.2)
        self.play(ReplacementTransform(eye, text2), text1.animate.shift(UP*1.2), run_time=1.5)
        self.play(Write(text3), run_time=1.5)

        # ==========================================
        # ANIMATION 4 (0:06 - 0:09)
        # ==========================================
        text4 = Text("SAHI BAAT", font_size=70, color=GREEN, weight=BOLD).shift(UP*1)
        text5 = Text("Phir bhi...", font_size=40, color=WHITE)
        self.play(FadeOut(VGroup(text1, text2, text3)), FadeIn(text4, shift=UP), Write(text5), run_time=2)

        # ==========================================
        # ANIMATIONS 5-6 (0:09 - 0:12)
        # ==========================================
        text6 = Text("REJECTED!", font_size=90, color=RED, weight=BOLD)
        box = SurroundingRectangle(text6, color=RED, stroke_width=6, buff=0.3)
        self.play(ReplacementTransform(VGroup(text4, text5), text6), Create(box), run_time=1.5)
        self.play(Wiggle(VGroup(text6, box)), run_time=1.5)

        # ==========================================
        # ANIMATIONS 7-8 (0:12 - 0:16)
        # ==========================================
        text7 = Text("Communication Skills?", font_size=45, color=WHITE).shift(UP*1.5)
        text8 = Text("YA", font_size=30, color=GRAY)
        text9 = Text("DEEPER SCIENCE?", font_size=65, color="#00D4FF", weight=BOLD).shift(DOWN*1.5)
        self.play(FadeOut(VGroup(text6, box)), Write(text7), run_time=1)
        self.play(FadeIn(text8), Write(text9), run_time=2)

        # ==========================================
        # ANIMATION 9 (0:16 - 0:22)
        # ==========================================
        book1 = Text("How to Win Friends", font_size=60, color="#FFB800", weight=BOLD).shift(UP*0.5)
        book2 = Text("& Influence People", font_size=60, color="#FFB800", weight=BOLD).shift(DOWN*0.5)
        self.play(ReplacementTransform(VGroup(text7, text8, text9), VGroup(book1, book2)), run_time=3)

        # ==========================================
        # ANIMATIONS 10-11 (0:22 - 0:27)
        # ==========================================
        text10 = Text("MANIPULATE NAHI", font_size=70, color=RED, weight=BOLD)
        cross = Cross(text10, stroke_color=RED, stroke_width=15)
        self.play(FadeOut(VGroup(book1, book2)), FadeIn(text10, scale=0.5), run_time=1.5)
        self.play(Create(cross), run_time=1)

        # ==========================================
        # ANIMATIONS 12-13 (0:27 - 0:32)
        # ==========================================
        text11 = Text("GENUINELY SAMAJHNA", font_size=65, color="#00D4FF", weight=BOLD)
        self.play(ReplacementTransform(VGroup(text10, cross), text11), run_time=2)
        self.play(Indicate(text11, scale_factor=1.2, color="#FFB800"), run_time=2)

        # ==========================================
        # ANIMATION 14 (0:32 - 0:37)
        # ==========================================
        text12 = Text("BINA ARGUMENT", font_size=60, color=WHITE, weight=BOLD).shift(UP*1)
        text13 = Text("Apni baat rakhna", font_size=55, color="#FFB800").shift(DOWN*1)
        self.play(FadeOut(text11), FadeIn(text12, shift=DOWN), Write(text13), run_time=3)

        # ==========================================
        # ANIMATIONS 15-16 (0:37 - 0:43)
        # ==========================================
        text14 = Text("CRITICISM", font_size=70, color=RED, weight=BOLD).shift(LEFT*3)
        text15 = Text("INSPIRE", font_size=70, color=GREEN, weight=BOLD).shift(RIGHT*3)
        arrow = Arrow(text14.get_right(), text15.get_left(), color=WHITE, stroke_width=8)
        self.play(ReplacementTransform(VGroup(text12, text13), text14), run_time=1.5)
        self.play(GrowArrow(arrow), FadeIn(text15, shift=LEFT), run_time=2)

        # ==========================================
        # ANIMATIONS 17-18 (0:43 - 0:49)
        # ==========================================
        text16 = Text("MAKE THEM FEEL", font_size=50, color=WHITE).shift(UP*1)
        text17 = Text("IMPORTANT", font_size=90, color="#FFB800", weight=BOLD).shift(DOWN*0.5)
        self.play(FadeOut(VGroup(text14, arrow, text15)), Write(text16), run_time=1.5)
        self.play(FadeIn(text17, scale=2), run_time=2)

        # ==========================================
        # ANIMATIONS 19-20 (0:49 - 0:56)
        # ==========================================
        text18 = Text("EK MEETING TAK", font_size=50, color=GRAY, weight=BOLD)
        text19 = Text("LIMITED NAHI", font_size=70, color=RED, weight=BOLD).shift(DOWN*1)
        self.play(ReplacementTransform(VGroup(text16, text17), text18), run_time=2)
        self.play(Write(text19), run_time=2)

        # ==========================================
        # ANIMATIONS 21-22 (0:56 - 1:04)
        # ==========================================
        text20 = Text("SIMPLE CHANGES", font_size=65, color="#00D4FF", weight=BOLD).shift(UP*1)
        text21 = Text("COMPLETE SHIFT", font_size=80, color="#FFB800", weight=BOLD).shift(DOWN*1)
        self.play(FadeOut(VGroup(text18, text19)), FadeIn(text20, shift=UP), run_time=2)
        self.play(FadeIn(text21, shift=UP), run_time=2)
        
        # ==========================================
        # ANIMATION 23 (End fade)
        # ==========================================
        self.play(FadeOut(VGroup(text20, text21)), run_time=1)
