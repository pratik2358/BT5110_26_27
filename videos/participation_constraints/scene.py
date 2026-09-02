"""
Manim Community animation explaining ER participation constraints
(min, max) -- built to accompany BT5110 Tutorial 2 (the VINO tasting-
session schema). Every example reuses the VINO entities/relationships
from tut_02.tex so it reads as a continuation of that diagram.

Render all scenes and concatenate them into the final video with:

    bash render.sh

which produces docs/videos/tut_02_participation_constraints.mp4 for
the site.
"""

from manim import *

# ---------------------------------------------------------------------------
# Shared styling (mirrors the other videos for a consistent look)
# ---------------------------------------------------------------------------

ACCENT = "#6fa8dc"
ACCENT_SOFT = "#1b2733"
HL = "#f2c14e"
GOOD = "#89ca78"
BAD = "#e06c75"
MEMBER_FILL = "#2a1f2b"
MONO_FONT = "Menlo"

config.background_color = "#101114"


def data_table(data, col_labels, name=None, scale=0.5, name_color=ACCENT):
    table = Table(
        data,
        col_labels=[Text(c, font=MONO_FONT, weight=BOLD) for c in col_labels],
        include_outer_lines=True,
        line_config={"stroke_width": 1.5, "color": GREY_B},
    ).scale(scale)
    table.get_horizontal_lines().set_color(GREY_B)
    table.get_vertical_lines().set_color(GREY_B)
    group = table
    if name:
        cap = Text(name, font_size=28, color=name_color, weight=BOLD)
        cap.next_to(table, UP, buff=0.28)
        group = VGroup(table, cap)
    return group


class WatermarkedScene(Scene):
    def setup(self):
        super().setup()
        self.watermark = Text("Pratik Karmakar", font_size=16, color=GREY_C)
        self.watermark.set_opacity(0.45)
        self.watermark.to_corner(DR, buff=0.2)
        self.add(self.watermark)

    def clear_scene(self):
        self.play(*[
            FadeOut(m) for m in self.mobjects if m is not self.watermark
        ])


# ---------------------------------------------------------------------------
# ER-diagram building blocks (same conventions as videos/er_aggregation)
# ---------------------------------------------------------------------------

def entity_box(label, width=2.0, height=0.75, fill=ACCENT_SOFT, font_size=22):
    box = Rectangle(width=width, height=height, color=WHITE,
                     fill_color=fill, fill_opacity=1, stroke_width=2.5)
    text = Text(label, font_size=font_size, weight=BOLD, color=WHITE)
    text.move_to(box.get_center())
    group = VGroup(box, text)
    group.box = box
    return group


def rel_diamond(label, width=1.7, height=0.85, font_size=18, color=WHITE):
    diamond = Polygon(UP, RIGHT, DOWN, LEFT, color=color, stroke_width=2.5)
    diamond.stretch_to_fit_width(width)
    diamond.stretch_to_fit_height(height)
    text = Text(label, font_size=font_size, color=WHITE)
    text.move_to(diamond.get_center())
    group = VGroup(diamond, text)
    group.diamond = diamond
    return group


def hline(left_mobj, right_mobj, color=GREY_B, stroke_width=2):
    return Line(left_mobj.get_right(), right_mobj.get_left(),
                color=color, stroke_width=stroke_width)


def vline(top_mobj, bottom_mobj, color=GREY_B, stroke_width=2):
    return Line(top_mobj.get_bottom(), bottom_mobj.get_top(),
                color=color, stroke_width=stroke_width)


def card_label(text, mobj, direction=UP, buff=0.1, font_size=20,
               color=HL):
    t = Text(text, font_size=font_size, color=color, weight=BOLD)
    t.next_to(mobj, direction, buff=buff)
    return t


# ---------------------------------------------------------------------------
# Scene 1 -- Title
# ---------------------------------------------------------------------------

class S01_Title(WatermarkedScene):
    def construct(self):
        kicker = Text("BT5110 · Tutorial 2", font_size=28, color=ACCENT)
        title = Text("Participation Constraints", font_size=48, weight=BOLD)
        sub = Text(
            "What (min, max) actually means on a wire",
            font_size=26, color=GREY_B,
        )
        group = VGroup(kicker, title, sub).arrange(DOWN, buff=0.35)
        self.play(FadeIn(kicker, shift=UP * 0.2))
        self.play(Write(title))
        self.play(FadeIn(sub, shift=UP * 0.2))
        self.wait(1.2)
        self.play(FadeOut(group))


# ---------------------------------------------------------------------------
# Scene 2 -- What (min, max) means
# ---------------------------------------------------------------------------

class S02_WhatItMeans(WatermarkedScene):
    def construct(self):
        heading = Text("Two independent questions", font_size=32,
                        weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        entity = entity_box("A", width=1.4, height=0.7, font_size=22)
        diamond = rel_diamond("R", width=1.3, height=0.7, font_size=20)
        other = entity_box("B", width=1.4, height=0.7, font_size=22)
        row = VGroup(entity, diamond, other).arrange(RIGHT, buff=0.7)
        row.next_to(heading, DOWN, buff=0.5)
        line1 = hline(entity, diamond)
        line2 = hline(diamond, other)
        card = card_label("(min, max)", line1, UP, font_size=22)
        self.play(FadeIn(row), Create(line1), Create(line2))
        self.play(FadeIn(card, shift=UP * 0.2))
        self.wait(0.8)

        q1 = Text("min — must every entity take part at least once?",
                   font_size=24, color=WHITE)
        q1b = Text("0 = optional, can sit out      1 = mandatory",
                    font_size=22, color=GREY_B)
        q2 = Text("max — can one entity link to many R-instances?",
                   font_size=24, color=WHITE)
        q2b = Text("1 = at most one      n = as many as it likes",
                    font_size=22, color=GREY_B)
        qgroup = VGroup(q1, q1b, q2, q2b).arrange(DOWN, buff=0.22,
                                                    aligned_edge=LEFT)
        qgroup.next_to(row, DOWN, buff=0.6)
        self.play(FadeIn(qgroup, shift=UP * 0.2))
        self.wait(2.2)

        self.clear_scene()

        heading2 = Text("The four combinations", font_size=32, weight=BOLD)
        heading2.to_edge(UP)
        self.play(FadeIn(heading2, shift=UP * 0.2))

        def combo(label, desc, color):
            box = Rectangle(width=3.6, height=1.5, color=color,
                             stroke_width=2.5)
            tag = Text(label, font_size=32, weight=BOLD, color=color)
            d = Text(desc, font_size=18, color=GREY_B)
            content = VGroup(tag, d).arrange(DOWN, buff=0.15)
            content.move_to(box.get_center())
            return VGroup(box, content)

        c01 = combo("(0,1)", "optional · at most one", ACCENT)
        c11 = combo("(1,1)", "mandatory · exactly one", GOOD)
        c0n = combo("(0,n)", "optional · many allowed", ACCENT)
        c1n = combo("(1,n)", "mandatory · many allowed", GOOD)
        grid = VGroup(
            VGroup(c11, c0n).arrange(RIGHT, buff=0.6),
            VGroup(c1n, c01).arrange(RIGHT, buff=0.6),
        ).arrange(DOWN, buff=0.5)
        grid.next_to(heading2, DOWN, buff=0.6)
        self.play(FadeIn(grid, lag_ratio=0.15))
        self.wait(2.4)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 3 -- (1,1): mandatory, exactly one
# ---------------------------------------------------------------------------

class S03_OneOne(WatermarkedScene):
    def construct(self):
        heading = Text("(1,1) — mandatory, exactly one", font_size=30,
                        weight=BOLD, color=GOOD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        bottle = entity_box("bottle", width=1.9, height=0.72, font_size=20)
        contain = rel_diamond("contain", width=1.6, height=0.8, font_size=18)
        wine = entity_box("wine", width=1.9, height=0.72, font_size=20)
        row = VGroup(bottle, contain, wine).arrange(RIGHT, buff=0.7)
        row.next_to(heading, DOWN, buff=0.45)
        l1 = hline(bottle, contain)
        l2 = hline(contain, wine)
        self.play(FadeIn(row), Create(l1), Create(l2))
        c1 = card_label("(1,1)", l1, UP)
        c2 = card_label("(0,n)", l2, UP, color=GREY_B)
        self.play(FadeIn(c1), FadeIn(c2))
        self.wait(0.8)

        bottle_cols = ["wine", "number"]
        bottle_rows = [
            ["Rumbalara", "1"],
            ["Rumbalara", "2"],
            ["Cuvée Noir", "1"],
            ["Cuvée Noir", "2"],
        ]
        table = data_table(bottle_rows, bottle_cols, scale=0.55, name="bottle")
        table.next_to(row, DOWN, buff=0.55)
        self.play(Create(table))
        self.wait(0.5)

        t = table[0]
        for r in range(len(bottle_rows)):
            t.get_entries((r + 2, 1)).set_color(GOOD)
        self.wait(0.4)

        note = Text(
            "Every bottle names exactly one wine — never empty, never two",
            font_size=22, color=GOOD,
        )
        note.next_to(table, DOWN, buff=0.4)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 4 -- (0,1): optional, at most one
# ---------------------------------------------------------------------------

class S04_ZeroOne(WatermarkedScene):
    def construct(self):
        heading = Text("(0,1) — optional, at most one", font_size=30,
                        weight=BOLD, color=ACCENT)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        bottle = entity_box("bottle", width=1.9, height=0.72, font_size=20)
        opened = rel_diamond("opened", width=1.6, height=0.8, font_size=18)
        session = entity_box("session", width=1.9, height=0.72, font_size=20)
        row = VGroup(bottle, opened, session).arrange(RIGHT, buff=0.7)
        row.next_to(heading, DOWN, buff=0.45)
        l1 = hline(bottle, opened)
        l2 = hline(opened, session)
        self.play(FadeIn(row), Create(l1), Create(l2))
        c1 = card_label("(0,1)", l1, UP)
        c2 = card_label("(0,n)", l2, UP, color=GREY_B)
        self.play(FadeIn(c1), FadeIn(c2))
        self.wait(0.8)

        bottle_cols = ["wine", "number"]
        bottle_rows = [
            ["Rumbalara", "1"],
            ["Rumbalara", "2"],
            ["Cuvée Noir", "1"],
            ["Cuvée Noir", "2"],
        ]
        open_cols = ["wine", "number", "session"]
        open_rows = [
            ["Rumbalara", "1", "S1"],
            ["Rumbalara", "2", "S1"],
            ["Cuvée Noir", "1", "S2"],
        ]
        bt = data_table(bottle_rows, bottle_cols, scale=0.48, name="bottle")
        ot = data_table(open_rows, open_cols, scale=0.48, name="open")
        both = VGroup(bt, ot).arrange(RIGHT, buff=1.0, aligned_edge=UP)
        both.next_to(row, DOWN, buff=0.5)
        self.play(Create(bt), Create(ot))
        self.wait(0.6)

        bt_table = bt[0]
        for r in range(3):
            for c in [1, 2]:
                bt_table.get_entries((r + 2, c)).set_color(GOOD)
        missing_row = VGroup(*[bt_table.get_entries((5, c)) for c in [1, 2]])
        missing_row.set_color(BAD)
        box = SurroundingRectangle(missing_row, color=BAD, buff=0.06)
        self.play(Create(box))
        self.wait(0.4)

        note = Text(
            "Cuvée Noir #2 never shows up in open — still in the cellar",
            font_size=21, color=BAD,
        )
        note2 = Text(
            "the other three appear exactly once — never twice",
            font_size=21, color=GOOD,
        )
        notes = VGroup(note, note2).arrange(DOWN, buff=0.15)
        notes.next_to(both, DOWN, buff=0.4)
        self.play(FadeIn(notes, shift=UP * 0.2))
        self.wait(2.2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 5 -- (1,n): mandatory, many allowed
# ---------------------------------------------------------------------------

class S05_OneN(WatermarkedScene):
    def construct(self):
        heading = Text("(1,n) — mandatory, many allowed", font_size=30,
                        weight=BOLD, color=GOOD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        opened = rel_diamond("opened bottle", width=2.2, height=0.85,
                              font_size=17)
        tasted = rel_diamond("tasted", width=1.6, height=0.8, font_size=18)
        member = entity_box("member", width=1.9, height=0.72, font_size=20,
                             fill=MEMBER_FILL)
        row = VGroup(opened, tasted, member).arrange(RIGHT, buff=0.7)
        row.next_to(heading, DOWN, buff=0.45)
        l1 = hline(opened, tasted)
        l2 = hline(tasted, member)
        self.play(FadeIn(row), Create(l1), Create(l2))
        c1 = card_label("(1,n)", l1, UP)
        c2 = card_label("(0,n)", l2, UP, color=GREY_B)
        self.play(FadeIn(c1), FadeIn(c2))
        self.wait(0.8)

        taste_cols = ["member", "wine", "number", "rating"]
        taste_rows = [
            ["Alice", "Rumbalara", "1", "Good"],
            ["Bob", "Rumbalara", "1", "Very Good"],
            ["Alice", "Rumbalara", "2", "Average"],
            ["Carol", "Cuvée Noir", "1", "Good"],
        ]
        table = data_table(taste_rows, taste_cols, scale=0.5, name="taste")
        table.next_to(row, DOWN, buff=0.55)
        self.play(Create(table))
        self.wait(0.5)

        t = table[0]
        pair_box = SurroundingRectangle(
            VGroup(*[t.get_entries((r, c)) for r in [2, 3] for c in [2, 3]]),
            color=GOOD, buff=0.06,
        )
        self.play(Create(pair_box))
        self.wait(0.4)

        note = Text(
            "Every opened bottle — Rumbalara #1, #2, Cuvée Noir #1 — appears\n"
            "at least once here. Rumbalara #1 was tasted by two members.",
            font_size=21, color=GOOD, line_spacing=1.3,
        )
        note.next_to(table, DOWN, buff=0.4)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(2.4)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 6 -- (0,n): optional, many allowed
# ---------------------------------------------------------------------------

class S06_ZeroN(WatermarkedScene):
    def construct(self):
        heading = Text("(0,n) — optional, many allowed", font_size=30,
                        weight=BOLD, color=ACCENT)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        member = entity_box("member", width=1.9, height=0.72, font_size=20,
                             fill=MEMBER_FILL)
        tasted = rel_diamond("tasted", width=1.6, height=0.8, font_size=18)
        opened = rel_diamond("opened bottle", width=2.2, height=0.85,
                              font_size=17)
        row = VGroup(member, tasted, opened).arrange(RIGHT, buff=0.7)
        row.next_to(heading, DOWN, buff=0.45)
        l1 = hline(member, tasted)
        l2 = hline(tasted, opened)
        self.play(FadeIn(row), Create(l1), Create(l2))
        c1 = card_label("(0,n)", l1, UP)
        c2 = card_label("(1,n)", l2, UP, color=GREY_B)
        self.play(FadeIn(c1), FadeIn(c2))
        self.wait(0.8)

        member_cols = ["member"]
        member_rows = [["Alice"], ["Bob"], ["Carol"], ["Dave"]]
        taste_cols = ["member", "wine", "number"]
        taste_rows = [
            ["Alice", "Rumbalara", "1"],
            ["Bob", "Rumbalara", "1"],
            ["Alice", "Rumbalara", "2"],
            ["Carol", "Cuvée Noir", "1"],
        ]
        mt = data_table(member_rows, member_cols, scale=0.5, name="member")
        tt = data_table(taste_rows, taste_cols, scale=0.5, name="taste")
        both = VGroup(mt, tt).arrange(RIGHT, buff=1.0, aligned_edge=UP)
        both.next_to(row, DOWN, buff=0.5)
        self.play(Create(mt), Create(tt))
        self.wait(0.5)

        mtable = mt[0]
        dave = mtable.get_entries((5, 1))
        dave_box = SurroundingRectangle(dave, color=BAD, buff=0.06)
        alice = mtable.get_entries((2, 1))
        alice_box = SurroundingRectangle(alice, color=GOOD, buff=0.06)
        self.play(Create(dave_box), Create(alice_box))
        self.wait(0.4)

        note = Text(
            "Dave hasn't tasted anything yet — zero rows in taste",
            font_size=21, color=BAD,
        )
        note2 = Text(
            "Alice shows up twice — both are valid participation counts",
            font_size=21, color=GOOD,
        )
        notes = VGroup(note, note2).arrange(DOWN, buff=0.15)
        notes.next_to(both, DOWN, buff=0.4)
        self.play(FadeIn(notes, shift=UP * 0.2))
        self.wait(2.4)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 7 -- Synthesis: all four in the VINO diagram
# ---------------------------------------------------------------------------

class S07_Synthesis(WatermarkedScene):
    def construct(self):
        heading = Text("All four, in one diagram", font_size=30,
                        weight=BOLD)
        heading.to_edge(UP, buff=0.3)
        self.play(FadeIn(heading, shift=UP * 0.2))

        ew, eh, ef = 1.6, 0.58, 16
        dw, dh, df = 1.35, 0.65, 14

        session = entity_box("session", width=ew, height=eh, font_size=ef)
        opened = rel_diamond("opened", width=dw, height=dh, font_size=df)
        bottle = entity_box("bottle", width=ew, height=eh, font_size=ef)
        top = VGroup(session, opened, bottle).arrange(RIGHT, buff=0.85)
        top.move_to(UP * 1.6 + LEFT * 1.2)

        contain = rel_diamond("contain", width=dw, height=dh, font_size=df)
        wine = entity_box("wine", width=ew, height=eh, font_size=ef)
        contain.next_to(bottle, DOWN, buff=0.65)
        wine.next_to(contain, DOWN, buff=0.65)

        tasted = rel_diamond("tasted", width=dw, height=dh, font_size=df)
        member = entity_box("member", width=ew, height=eh, font_size=ef,
                             fill=MEMBER_FILL)
        tasted.next_to(opened, DOWN, buff=0.65)
        member.next_to(tasted, DOWN, buff=0.65)

        agg_box = SurroundingRectangle(opened, color=WHITE, buff=0.28,
                                        corner_radius=0.08, stroke_width=2)

        lines = VGroup(
            hline(session, opened), hline(opened, bottle),
            vline(bottle, contain), vline(contain, wine),
            vline(agg_box, tasted), vline(tasted, member),
        )

        diagram = VGroup(session, opened, bottle, contain, wine, tasted,
                          member, agg_box, lines)
        self.play(FadeIn(session), FadeIn(bottle), FadeIn(wine),
                   FadeIn(member))
        self.play(Create(lines[0]), Create(lines[1]), FadeIn(opened))
        self.play(Create(lines[2]), Create(lines[3]), FadeIn(contain))
        self.play(Create(agg_box))
        self.play(Create(lines[4]), Create(lines[5]), FadeIn(tasted))
        self.wait(0.4)

        c1 = card_label("(0,n)", lines[0], UP, font_size=15, color=ACCENT)
        c2 = card_label("(0,1)", lines[1], UP, font_size=15, color=ACCENT)
        c3 = card_label("(1,1)", lines[2], RIGHT, buff=0.1, font_size=15,
                         color=GOOD)
        c4 = card_label("(0,n)", lines[3], RIGHT, buff=0.1, font_size=15,
                         color=ACCENT)
        c5 = card_label("(1,n)", lines[4], LEFT, buff=0.1, font_size=15,
                         color=GOOD)
        c6 = card_label("(0,n)", lines[5], LEFT, buff=0.1, font_size=15,
                         color=ACCENT)
        cards = VGroup(c1, c2, c3, c4, c5, c6)
        self.play(FadeIn(cards, lag_ratio=0.1))
        self.wait(1.4)

        legend1 = VGroup(
            Text("●", font_size=18, color=GOOD),
            Text("mandatory", font_size=19, color=GREY_B),
        ).arrange(RIGHT, buff=0.12)
        legend2 = VGroup(
            Text("●", font_size=18, color=ACCENT),
            Text("optional", font_size=19, color=GREY_B),
        ).arrange(RIGHT, buff=0.12)
        legend = VGroup(legend1, legend2).arrange(RIGHT, buff=0.6)
        legend.next_to(diagram, DOWN, buff=0.4)
        self.play(FadeIn(legend, shift=UP * 0.2))
        self.wait(2.4)

        self.clear_scene()
