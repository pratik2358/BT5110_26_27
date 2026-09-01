"""
Manim Community animation explaining Relational Algebra, built to accompany
BT5110 Tutorial 1 (Relational Model).

Render all scenes and concatenate them into the final video with:

    bash render.sh

which produces docs/videos/tut_01_relational_algebra.mp4 for the site.
"""

from manim import *

# ---------------------------------------------------------------------------
# Shared styling
# ---------------------------------------------------------------------------

ACCENT = "#6fa8dc"       # matches the site's dark-mode accent colour
ACCENT_SOFT = "#1b2733"
HL = "#f2c14e"            # highlight yellow, used for matched rows/cols
HL2 = "#e06c75"           # secondary highlight, used for join keys
SQL_KEYWORDS = [
    "SELECT", "FROM", "WHERE", "JOIN", "ON", "CROSS", "AND", "OR",
    "INNER", "AS",
]
MONO_FONT = "Menlo"

config.background_color = "#101114"


def sql_block(lines, font_size=28, highlight_lines=None):
    """A left-aligned, syntax-tinted block of SQL text."""
    highlight_lines = highlight_lines or {}
    t2c = {kw: "#c586c0" for kw in SQL_KEYWORDS}
    rows = VGroup()
    for i, line in enumerate(lines):
        t2c_line = dict(t2c)
        if i in highlight_lines:
            for token in highlight_lines[i]:
                t2c_line[token] = HL
        txt = Text(line, font=MONO_FONT, font_size=font_size, t2c=t2c_line)
        rows.add(txt)
    rows.arrange(DOWN, aligned_edge=LEFT, buff=0.18)
    return rows


def ra_expr(tex, font_size=40, color=WHITE):
    return MathTex(tex, font_size=font_size, color=color)


def labelled_box(mobj, label, color=ACCENT):
    """Wrap a mobject with a small caption above it, e.g. 'PostgreSQL'."""
    cap = Text(label, font_size=24, color=color, weight=BOLD)
    group = VGroup(cap, mobj).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
    return group


def relation_table(data, col_labels, name=None, scale=0.6,
                    row_highlight=None, col_highlight=None,
                    cell_highlight=None):
    row_highlight = row_highlight or []
    col_highlight = col_highlight or []
    cell_highlight = cell_highlight or {}
    table = Table(
        data,
        col_labels=[Text(c, font=MONO_FONT, weight=BOLD) for c in col_labels],
        include_outer_lines=True,
        line_config={"stroke_width": 1.5, "color": GREY_B},
    ).scale(scale)
    table.get_horizontal_lines().set_color(GREY_B)
    table.get_vertical_lines().set_color(GREY_B)

    for r in row_highlight:
        table.add_highlighted_cell((r + 2, 1), color=ACCENT_SOFT)
        for c in range(1, len(col_labels) + 1):
            table.add_highlighted_cell((r + 2, c), color=ACCENT_SOFT)
    for c in col_highlight:
        for r in range(1, len(data) + 2):
            table.add_highlighted_cell((r, c + 1), color=ACCENT_SOFT)
    for (r, c), color in cell_highlight.items():
        table.add_highlighted_cell((r + 2, c + 1), color=color)

    group = table
    if name:
        cap = Text(name, font_size=32, color=ACCENT, weight=BOLD)
        cap.next_to(table, UP, buff=0.35)
        group = VGroup(table, cap)
    return group


# ---------------------------------------------------------------------------
# Data used throughout the video
# ---------------------------------------------------------------------------

STUDENT_COLS = ["sid", "sname", "age", "major"]
STUDENT_ROWS = [
    ["1", "Alice", "21", "CS"],
    ["2", "Bob", "22", "EE"],
    ["3", "Carol", "20", "CS"],
    ["4", "Dave", "23", "ME"],
]

ENROLL_COLS = ["sid", "cid", "grade"]
ENROLL_ROWS = [
    ["1", "CS101", "A"],
    ["1", "CS102", "B"],
    ["2", "EE101", "A"],
    ["3", "CS101", "B"],
]


# ---------------------------------------------------------------------------
# Scene 1 -- Title
# ---------------------------------------------------------------------------

class S01_Title(Scene):
    def construct(self):
        kicker = Text("BT5110 · Tutorial 1", font_size=28, color=ACCENT)
        title = Text("Relational Algebra", font_size=56, weight=BOLD)
        sub = Text(
            "From tables to queries, one operation at a time",
            font_size=26, color=GREY_B,
        )
        group = VGroup(kicker, title, sub).arrange(DOWN, buff=0.35)
        self.play(FadeIn(kicker, shift=UP * 0.2))
        self.play(Write(title))
        self.play(FadeIn(sub, shift=UP * 0.2))
        self.wait(1.2)
        self.play(FadeOut(group))


# ---------------------------------------------------------------------------
# Scene 2 -- Introduce a relation
# ---------------------------------------------------------------------------

class S02_IntroRelation(Scene):
    def construct(self):
        heading = Text("A table is a relation", font_size=36, weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        table_group = relation_table(STUDENT_ROWS, STUDENT_COLS, scale=0.68)
        table_group.to_edge(LEFT, buff=1.0).shift(DOWN * 0.3)
        self.play(Create(table_group))
        self.wait(0.5)

        name_tex = MathTex(
            r"R = \text{Student}(\mathit{sid}, \mathit{sname}, "
            r"\mathit{age}, \mathit{major})",
            font_size=30,
        )
        name_tex.next_to(table_group, UP, buff=0.5).align_to(table_group, LEFT)
        self.play(FadeOut(heading), Write(name_tex))
        self.wait(0.8)

        # Highlight a row -> tuple
        table = table_group
        row_rect = SurroundingRectangle(
            VGroup(*[table.get_entries((3, c)) for c in range(1, 5)]),
            color=HL, buff=0.12,
        )
        tuple_label = Text("a row = a tuple", font_size=26, color=HL)
        tuple_label.to_edge(RIGHT, buff=0.9).shift(UP * 1.2)
        arrow1 = Arrow(tuple_label.get_left(), row_rect.get_right(),
                        color=HL, buff=0.15, stroke_width=3)
        self.play(Create(row_rect))
        self.play(FadeIn(tuple_label), GrowArrow(arrow1))
        self.wait(1)
        self.play(FadeOut(row_rect), FadeOut(tuple_label), FadeOut(arrow1))

        # Highlight a column -> attribute
        col_rect = SurroundingRectangle(
            VGroup(*[table.get_entries((r, 4)) for r in range(1, 6)]),
            color=ACCENT, buff=0.1,
        )
        col_label = Text("a column = an attribute", font_size=26, color=ACCENT)
        col_label.to_edge(RIGHT, buff=0.9).shift(DOWN * 0.8)
        arrow2 = Arrow(col_label.get_left(), col_rect.get_right(),
                        color=ACCENT, buff=0.15, stroke_width=3)
        self.play(Create(col_rect))
        self.play(FadeIn(col_label), GrowArrow(arrow2))
        self.wait(1.2)

        self.play(*[FadeOut(m) for m in self.mobjects])


# ---------------------------------------------------------------------------
# Scene 3 -- Selection
# ---------------------------------------------------------------------------

class S03_Selection(Scene):
    def construct(self):
        heading = Text("Selection  —  filters rows", font_size=34, weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        table_group = relation_table(STUDENT_ROWS, STUDENT_COLS, scale=0.62,
                                      name="R (Student)")
        table_group.to_edge(LEFT, buff=0.9).shift(DOWN * 0.3)
        self.play(Create(table_group))

        ra = ra_expr(r"\sigma_{\,\mathit{major}\,=\,'CS'}(R)")
        sql = sql_block(
            ["SELECT *", "FROM Student", "WHERE major = 'CS';"],
            highlight_lines={2: ["major", "'CS'"]},
        )
        panel = VGroup(
            labelled_box(ra, "Relational Algebra"),
            labelled_box(sql, "PostgreSQL"),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.6)
        panel.to_edge(RIGHT, buff=0.8).shift(DOWN * 0.1)
        self.play(FadeIn(panel, shift=LEFT * 0.2))
        self.wait(1)

        table = table_group[0]
        cs_rows = [0, 2]  # 0-indexed data rows matching major == CS
        rects = VGroup(*[
            SurroundingRectangle(
                VGroup(*[table.get_entries((r + 2, c)) for c in range(1, 5)]),
                color=HL, buff=0.08,
            ) for r in cs_rows
        ])
        self.play(Create(rects))
        self.wait(0.6)

        other_rows = VGroup(*[
            VGroup(*[table.get_entries((r + 2, c)) for c in range(1, 5)])
            for r in range(4) if r not in cs_rows
        ])
        self.play(other_rows.animate.set_opacity(0.15))
        self.wait(1)

        result_cap = Text("Result: rows kept where the predicate holds",
                           font_size=26, color=HL)
        result_cap.next_to(table_group, DOWN, buff=0.5)
        self.play(FadeIn(result_cap, shift=UP * 0.2))
        self.wait(1.4)

        self.play(*[FadeOut(m) for m in self.mobjects])


# ---------------------------------------------------------------------------
# Scene 4 -- Projection
# ---------------------------------------------------------------------------

class S04_Projection(Scene):
    def construct(self):
        heading = Text("Projection  —  selects columns", font_size=34, weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        table_group = relation_table(STUDENT_ROWS, STUDENT_COLS, scale=0.62,
                                      name="R (Student)")
        table_group.to_edge(LEFT, buff=0.9).shift(DOWN * 0.3)
        self.play(Create(table_group))

        ra = ra_expr(r"\pi_{\,\mathit{sname},\ \mathit{major}}(R)")
        sql = sql_block(
            ["SELECT sname, major", "FROM Student;"],
            highlight_lines={0: ["sname", "major"]},
        )
        panel = VGroup(
            labelled_box(ra, "Relational Algebra"),
            labelled_box(sql, "PostgreSQL"),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.6)
        panel.to_edge(RIGHT, buff=0.8).shift(DOWN * 0.1)
        self.play(FadeIn(panel, shift=LEFT * 0.2))
        self.wait(1)

        table = table_group[0]
        keep_cols = [2, 4]   # sname, major
        drop_cols = [1, 3]   # sid, age
        drop_group = VGroup(*[
            VGroup(*[table.get_entries((r, c)) for r in range(1, 6)])
            for c in drop_cols
        ])
        keep_rects = VGroup(*[
            SurroundingRectangle(
                VGroup(*[table.get_entries((r, c)) for r in range(1, 6)]),
                color=HL, buff=0.06,
            ) for c in keep_cols
        ])
        self.play(Create(keep_rects))
        self.play(drop_group.animate.set_opacity(0.12))
        self.wait(1.2)

        result_cap = Text("Result: only the listed columns remain",
                           font_size=26, color=HL)
        result_cap.next_to(table_group, DOWN, buff=0.5)
        self.play(FadeIn(result_cap, shift=UP * 0.2))
        self.wait(1.4)

        self.play(*[FadeOut(m) for m in self.mobjects])


# ---------------------------------------------------------------------------
# Scene 5 -- Composing selection + projection
# ---------------------------------------------------------------------------

class S05_Compose(Scene):
    def construct(self):
        heading = Text("Operations compose", font_size=34, weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        ra = ra_expr(
            r"\pi_{\,\mathit{sname}}\big(\sigma_{\,\mathit{major}='CS'}(R)\big)",
            font_size=44,
        )
        sql = sql_block([
            "SELECT sname",
            "FROM Student",
            "WHERE major = 'CS';",
        ], highlight_lines={0: ["sname"], 2: ["major", "'CS'"]})

        panel = VGroup(
            labelled_box(ra, "Relational Algebra"),
            labelled_box(sql, "PostgreSQL"),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.7)
        panel.move_to(ORIGIN)
        self.play(FadeIn(panel))
        self.wait(1)

        note = Text(
            "Selection first narrows the rows, then projection narrows the columns",
            font_size=24, color=GREY_B,
        )
        note.next_to(panel, DOWN, buff=0.7)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(1.6)

        self.play(*[FadeOut(m) for m in self.mobjects])


# ---------------------------------------------------------------------------
# Scene 6 -- A second relation
# ---------------------------------------------------------------------------

class S06_SecondTable(Scene):
    def construct(self):
        heading = Text("Bring in a second relation", font_size=34, weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        r_group = relation_table(STUDENT_ROWS, STUDENT_COLS, scale=0.55,
                                  name="R (Student)")
        s_group = relation_table(ENROLL_ROWS, ENROLL_COLS, scale=0.55,
                                  name="S (Enrollment)")
        both = VGroup(r_group, s_group).arrange(RIGHT, buff=1.4)
        both.move_to(ORIGIN).shift(DOWN * 0.2)

        self.play(Create(r_group))
        self.play(Create(s_group))
        self.wait(1)

        note = Text("R and S share the attribute sid",
                     font_size=26, color=ACCENT)
        note.next_to(both, DOWN, buff=0.6)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(1.4)

        self.play(*[FadeOut(m) for m in self.mobjects])


# ---------------------------------------------------------------------------
# Scene 7 -- Cross join
# ---------------------------------------------------------------------------

class S07_CrossJoin(Scene):
    def construct(self):
        heading = Text("Cross Join  —  every pairing", font_size=34, weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        r_group = relation_table(STUDENT_ROWS, STUDENT_COLS, scale=0.38,
                                  name="R")
        s_group = relation_table(ENROLL_ROWS, ENROLL_COLS, scale=0.38,
                                  name="S")
        times = MathTex(r"\times", font_size=42)
        tables_row = VGroup(r_group, times, s_group).arrange(RIGHT, buff=0.5)
        tables_row.next_to(heading, DOWN, buff=0.4)
        self.play(FadeIn(tables_row))

        ra = ra_expr(r"R \times S", font_size=32)
        sql = sql_block([
            "SELECT *",
            "FROM Student",
            "CROSS JOIN Enrollment;",
        ], font_size=24, highlight_lines={2: ["CROSS", "JOIN"]})
        panel = VGroup(
            labelled_box(ra, "Relational Algebra"),
            labelled_box(sql, "PostgreSQL"),
        ).arrange(RIGHT, buff=1.0)
        panel.next_to(tables_row, DOWN, buff=0.45)
        self.play(FadeIn(panel, shift=UP * 0.2))
        self.wait(1)

        count = MathTex(
            r"|R \times S| = |R| \cdot |S| = 4 \times 4 = 16 \text{ rows}",
            font_size=28, color=HL,
        )
        count.next_to(panel, DOWN, buff=0.45)
        self.play(FadeIn(count, shift=UP * 0.2))
        self.wait(1.6)

        result_note = Text(
            "Every row of R is paired with every row of S",
            font_size=22, color=GREY_B,
        )
        result_note.next_to(count, DOWN, buff=0.35)
        self.play(FadeIn(result_note, shift=UP * 0.2))
        self.wait(1.2)

        self.play(*[FadeOut(m) for m in self.mobjects])

        # --- Show the full 16-row result ---
        heading2 = Text("Result of R × S  —  all 16 rows", font_size=32,
                         weight=BOLD)
        heading2.to_edge(UP)
        self.play(FadeIn(heading2, shift=UP * 0.2))

        cross_cols = ["R.sid", "R.sname", "R.age", "R.major",
                      "S.sid", "S.cid", "S.grade"]
        cross_data = [r + s for r in STUDENT_ROWS for s in ENROLL_ROWS]
        cross_group = relation_table(cross_data, cross_cols, scale=0.27,
                                      name="R × S")
        cross_group.next_to(heading2, DOWN, buff=0.3)
        self.play(Create(cross_group))
        self.wait(1.8)

        note = Text(
            "Most of these pairings are meaningless — that's why we filter with a condition",
            font_size=20, color=GREY_B,
        )
        note.next_to(cross_group, DOWN, buff=0.3)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(1.8)

        self.play(*[FadeOut(m) for m in self.mobjects])


# ---------------------------------------------------------------------------
# Scene 8 -- Theta / equi join
# ---------------------------------------------------------------------------

class S08_ThetaJoin(Scene):
    def construct(self):
        heading = Text("Join with a condition", font_size=34, weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        r_group = relation_table(STUDENT_ROWS, STUDENT_COLS, scale=0.36,
                                  name="R", col_highlight=[0])
        s_group = relation_table(ENROLL_ROWS, ENROLL_COLS, scale=0.36,
                                  name="S", col_highlight=[0])
        both = VGroup(r_group, s_group).arrange(RIGHT, buff=1.3)
        both.next_to(heading, DOWN, buff=0.35)
        self.play(Create(both))

        ra = ra_expr(r"R \Join_{\,R.\mathit{sid}\,=\,S.\mathit{sid}}\, S",
                     font_size=30)
        sql = sql_block([
            "SELECT *",
            "FROM Student",
            "JOIN Enrollment",
            "  ON Student.sid = Enrollment.sid;",
        ], font_size=22, highlight_lines={2: ["JOIN"], 3: ["ON"]})
        panel = VGroup(
            labelled_box(ra, "Relational Algebra"),
            labelled_box(sql, "PostgreSQL"),
        ).arrange(RIGHT, buff=1.0)
        panel.next_to(both, DOWN, buff=0.4)
        self.play(FadeIn(panel, shift=UP * 0.2))
        self.wait(1.2)

        note = Text("Keep only the pairings whose sid columns match",
                     font_size=22, color=HL)
        note.next_to(panel, DOWN, buff=0.3)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(1.4)

        self.play(*[FadeOut(m) for m in self.mobjects])

        heading2 = Text("Result of the join", font_size=34, weight=BOLD)
        heading2.to_edge(UP)
        self.play(FadeIn(heading2, shift=UP * 0.2))

        condition = ra_expr(r"R \Join_{\,R.\mathit{sid}\,=\,S.\mathit{sid}}\, S",
                             font_size=30, color=ACCENT)
        condition.next_to(heading2, DOWN, buff=0.3)
        self.play(Write(condition))
        self.wait(0.6)

        result_data = [
            ["1", "Alice", "21", "CS", "CS101", "A"],
            ["1", "Alice", "21", "CS", "CS102", "B"],
            ["2", "Bob", "22", "EE", "EE101", "A"],
            ["3", "Carol", "20", "CS", "CS101", "B"],
        ]
        result_cols = ["sid", "sname", "age", "major", "cid", "grade"]
        result_group = relation_table(result_data, result_cols, scale=0.5,
                                       name="R ⋈ S")
        result_group.next_to(condition, DOWN, buff=0.45)
        self.play(Create(result_group))
        self.wait(1.6)

        self.play(*[FadeOut(m) for m in self.mobjects])


# ---------------------------------------------------------------------------
# Scene 9 -- A larger query, decomposed
# ---------------------------------------------------------------------------

class S09_FinalQuery(Scene):
    def construct(self):
        heading = Text("Putting it all together", font_size=34, weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        goal = Text(
            "Goal: names of students who scored an A in CS101",
            font_size=26, color=ACCENT,
        )
        goal.next_to(heading, DOWN, buff=0.3)
        self.play(FadeIn(goal, shift=UP * 0.2))

        ra_full = ra_expr(
            r"\pi_{\,\mathit{sname}}\Big(\sigma_{\,\mathit{grade}='A'\ \land\ "
            r"\mathit{cid}='CS101'}\big(R \Join_{\,\mathit{sid}} S\big)\Big)",
            font_size=28,
        )
        ra_full.next_to(goal, DOWN, buff=0.4)
        self.play(Write(ra_full))
        self.wait(1)

        sql_lines = [
            "SELECT s.sname",
            "FROM Student s",
            "JOIN Enrollment e",
            "  ON s.sid = e.sid",
            "WHERE e.grade = 'A'",
            "  AND e.cid = 'CS101';",
        ]
        sql = sql_block(sql_lines, font_size=24)
        sql_panel = labelled_box(sql, "PostgreSQL")
        sql_panel.next_to(ra_full, DOWN, buff=0.55).to_edge(LEFT, buff=1.4)
        self.play(FadeIn(sql_panel, shift=RIGHT * 0.2))
        self.wait(0.6)

        # Move the full RA expression out of the way, leaving room on the
        # right for each step's fragment while the SQL stays put on the left.
        ra_full_original = ra_full.copy()
        self.play(ra_full.animate.scale(0.75).to_corner(UR, buff=0.4))

        lines = sql_panel[1]  # the VGroup of Text lines
        step_anchor = RIGHT * 3.3 + DOWN * 1.0

        def flash(idx_list, color=HL):
            boxes = VGroup(*[
                SurroundingRectangle(lines[i], color=color, buff=0.06)
                for i in idx_list
            ])
            self.play(Create(boxes))
            return boxes

        def show_step(title, ra_tex, idx_list, ra_font_size=30):
            step_label = Text(title, font_size=24, color=HL)
            step_ra = ra_expr(ra_tex, font_size=ra_font_size, color=HL)
            step_group = VGroup(step_label, step_ra).arrange(DOWN, buff=0.35)
            step_group.move_to(step_anchor)
            boxes = flash(idx_list)
            self.play(FadeIn(step_group, shift=UP * 0.2))
            self.wait(1.4)
            self.play(FadeOut(boxes), FadeOut(step_group))

        # --- Step 1: the join ---
        show_step("Step 1 — Join Student and Enrollment on sid",
                   r"R \Join_{\,\mathit{sid}} S", [1, 2, 3])

        # --- Step 2: the selection ---
        show_step("Step 2 — Keep grade-A rows in CS101",
                   r"\sigma_{\,\mathit{grade}='A'\ \land\ \mathit{cid}='CS101'}(\cdot)",
                   [4, 5], ra_font_size=26)

        # --- Step 3: the projection ---
        show_step("Step 3 — Project just sname",
                   r"\pi_{\,\mathit{sname}}(\cdot)", [0])

        # Close on the full composite query -- SQL alongside its RA
        # expression -- as the final beat of the video.
        self.play(ra_full.animate.become(ra_full_original))
        self.wait(2.5)

        self.play(*[FadeOut(m) for m in self.mobjects])
