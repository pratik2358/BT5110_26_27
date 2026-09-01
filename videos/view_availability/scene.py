"""
Manim Community animation explaining how a view + EXISTS can replace a
redundant, stale column -- built to accompany BT5110 Tutorial 1's
"Drop Redundant Availability" question (see tut_01.tex, Q3a).

Render all scenes and concatenate them into the final video with:

    bash render.sh

which produces docs/videos/tut_01_view_availability.mp4 for the site.
"""

from manim import *

# ---------------------------------------------------------------------------
# Shared styling (mirrors videos/relational_algebra/scene.py for a
# consistent look across the site's videos)
# ---------------------------------------------------------------------------

ACCENT = "#6fa8dc"
ACCENT_SOFT = "#1b2733"
HL = "#f2c14e"          # highlight yellow -- "look here"
GOOD = "#89ca78"         # available / TRUE
BAD = "#e06c75"          # unavailable / FALSE, and warnings
MONO_FONT = "Menlo"

SQL_KEYWORDS = [
    "SELECT", "DISTINCT", "FROM", "WHERE", "AND", "OR",
    "CREATE", "REPLACE", "VIEW", "ALTER", "TABLE", "DROP", "COLUMN",
    "CASE", "WHEN", "THEN", "ELSE", "END", "EXISTS", "ISNULL",
]

config.background_color = "#101114"


def sql_block(lines, font_size=26, highlight_lines=None, dim_lines=None):
    """A left-aligned, syntax-tinted block of SQL text."""
    highlight_lines = highlight_lines or {}
    dim_lines = dim_lines or set()
    t2c = {kw: "#c586c0" for kw in SQL_KEYWORDS}
    rows = VGroup()
    for i, line in enumerate(lines):
        t2c_line = dict(t2c)
        if i in highlight_lines:
            for token in highlight_lines[i]:
                t2c_line[token] = HL
        color = GREY_C if i in dim_lines else WHITE
        txt = Text(line, font=MONO_FONT, font_size=font_size, t2c=t2c_line,
                    color=color)
        rows.add(txt)
    rows.arrange(DOWN, aligned_edge=LEFT, buff=0.16)
    return rows


def labelled_box(mobj, label, color=ACCENT):
    cap = Text(label, font_size=24, color=color, weight=BOLD)
    group = VGroup(cap, mobj).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
    return group


def book_header():
    """Column header for `book`, annotated as the FK it really is so
    viewers don't mistake it for a title -- it's book.isbn13."""
    top = Text("book", font=MONO_FONT, weight=BOLD)
    bottom = Text("(isbn13)", font=MONO_FONT, color=GREY_C, font_size=24)
    return VGroup(top, bottom).arrange(DOWN, buff=0.08)


def make_col_label(c):
    if c == "book":
        return book_header()
    return Text(c, font=MONO_FONT, weight=BOLD)


def data_table(data, col_labels, name=None, scale=0.5, name_color=ACCENT):
    table = Table(
        data,
        col_labels=[make_col_label(c) for c in col_labels],
        include_outer_lines=True,
        line_config={"stroke_width": 1.5, "color": GREY_B},
    ).scale(scale)
    table.get_horizontal_lines().set_color(GREY_B)
    table.get_vertical_lines().set_color(GREY_B)
    group = table
    if name:
        cap = Text(name, font_size=30, color=name_color, weight=BOLD)
        cap.next_to(table, UP, buff=0.3)
        group = VGroup(table, cap)
    return group


class WatermarkedScene(Scene):
    """Keeps a small, unobtrusive credit in the footnote corner for the
    whole scene, independent of whatever else fades in/out."""

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
# Data used throughout the video
# ---------------------------------------------------------------------------

COPY_COLS = ["owner", "book", "copy"]
COPY_ROWS = [
    ["alice", "B1", "1"],
    ["alice", "B2", "1"],
    ["bob", "B1", "1"],
    ["carol", "B3", "1"],
]

LOAN_COLS = ["borrower", "owner", "book", "copy", "borrowed", "returned"]
LOAN_ROWS = [
    ["dan", "alice", "B1", "1", "2026-01-05", "NULL"],
    ["eve", "alice", "B2", "1", "2025-11-01", "2025-11-20"],
    ["frank", "carol", "B3", "1", "2026-02-01", "NULL"],
]


def colour_returned_column(table_group, col_index=6, null_color=HL,
                            closed_color=GREY_B):
    """In the loan table, tint the `returned` column: NULL (open loan)
    in HL, an actual date (closed loan) in a muted colour."""
    table = table_group[0] if isinstance(table_group, VGroup) else table_group
    for r, row in enumerate(LOAN_ROWS):
        entry = table.get_entries((r + 2, col_index))
        if row[-1] == "NULL":
            entry.set_color(null_color)
        else:
            entry.set_color(closed_color)


# ---------------------------------------------------------------------------
# Scene 1 -- Title
# ---------------------------------------------------------------------------

class S01_Title(WatermarkedScene):
    def construct(self):
        kicker = Text("BT5110 · Tutorial 1", font_size=28, color=ACCENT)
        title = Text("Views & EXISTS", font_size=56, weight=BOLD)
        sub = Text(
            "Deriving availability instead of storing it",
            font_size=26, color=GREY_B,
        )
        group = VGroup(kicker, title, sub).arrange(DOWN, buff=0.35)
        self.play(FadeIn(kicker, shift=UP * 0.2))
        self.play(Write(title))
        self.play(FadeIn(sub, shift=UP * 0.2))
        self.wait(1.2)
        self.play(FadeOut(group))


# ---------------------------------------------------------------------------
# Scene 2 -- The problem with a stored `available` column
# ---------------------------------------------------------------------------

class S02_Problem(WatermarkedScene):
    def construct(self):
        heading = Text("A stored available column can lie", font_size=32,
                        weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        old_cols = ["owner", "book", "copy", "available"]
        old_rows = [
            ["alice", "B1", "1", "TRUE"],
            ["alice", "B2", "1", "FALSE"],
            ["bob", "B1", "1", "TRUE"],
            ["carol", "B3", "1", "TRUE"],
        ]
        table_group = data_table(old_rows, old_cols, scale=0.55,
                                  name="copy  (with the old column)")
        table_group.next_to(heading, DOWN, buff=0.5)
        self.play(Create(table_group))
        self.wait(0.6)

        table = table_group[0]
        stale_cell = table.get_entries((2, 4))
        stale_box = SurroundingRectangle(stale_cell, color=BAD, buff=0.08)
        stale_note = Text("stale: this copy actually has an open loan",
                           font_size=22, color=BAD)
        stale_note.next_to(table_group, DOWN, buff=0.45)
        self.play(Create(stale_box))
        self.play(FadeIn(stale_note, shift=UP * 0.2))
        self.wait(1.4)

        self.clear_scene()

        heading2 = Text("The rule that actually governs it", font_size=32,
                         weight=BOLD)
        heading2.to_edge(UP)
        self.play(FadeIn(heading2, shift=UP * 0.2))

        rule = Text(
            "A copy is unavailable  ⇔  it has an open (unreturned) loan",
            font_size=27, color=ACCENT,
        )
        rule.next_to(heading2, DOWN, buff=0.6)
        self.play(Write(rule))
        self.wait(1.2)

        sql = sql_block([
            "-- Remove the redundant column",
            "ALTER TABLE copy",
            "DROP COLUMN available;",
        ], font_size=28, highlight_lines={1: ["ALTER", "TABLE"],
                                           2: ["DROP", "COLUMN"]})
        sql.next_to(rule, DOWN, buff=0.7)
        self.play(FadeIn(sql, shift=UP * 0.2))
        self.wait(1.8)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 3 -- The working example data
# ---------------------------------------------------------------------------

class S03_SampleData(WatermarkedScene):
    def construct(self):
        heading = Text("Our working example", font_size=34, weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        copy_group = data_table(COPY_ROWS, COPY_COLS, scale=0.44, name="copy")
        loan_group = data_table(LOAN_ROWS, LOAN_COLS, scale=0.36, name="loan")
        both = VGroup(copy_group, loan_group).arrange(RIGHT, buff=0.9,
                                                        aligned_edge=UP)
        both.next_to(heading, DOWN, buff=0.5)
        self.play(Create(copy_group))
        self.play(Create(loan_group))
        colour_returned_column(loan_group)
        self.wait(0.6)

        legend_open = VGroup(
            Square(0.18, color=HL, fill_color=HL, fill_opacity=1),
            Text("returned = NULL  ->  open loan", font_size=20, color=HL),
        ).arrange(RIGHT, buff=0.15)
        legend_closed = VGroup(
            Square(0.18, color=GREY_B, fill_color=GREY_B, fill_opacity=1),
            Text("returned = a date  ->  closed loan", font_size=20,
                 color=GREY_B),
        ).arrange(RIGHT, buff=0.15)
        legend = VGroup(legend_open, legend_closed).arrange(DOWN, buff=0.2,
                                                              aligned_edge=LEFT)
        legend.next_to(loan_group, DOWN, buff=0.45).align_to(loan_group, LEFT)
        self.play(FadeIn(legend, shift=UP * 0.2))
        self.wait(1.8)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 4 -- Building the view: the skeleton
# ---------------------------------------------------------------------------

class S04_ViewSkeleton(WatermarkedScene):
    def construct(self):
        heading = Text("Step 1 — the view skeleton", font_size=32,
                        weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        sql = sql_block([
            "CREATE OR REPLACE VIEW copy_view",
            "  (owner, book, copy, available) AS (",
            "  SELECT DISTINCT c.owner, c.book, c.copy,",
            "    ⟨ availability logic ⟩",
            "  FROM copy c",
            ");",
        ], font_size=28, highlight_lines={
            0: ["CREATE", "REPLACE", "VIEW"],
            2: ["SELECT", "DISTINCT"],
            4: ["FROM"],
        }, dim_lines={3})
        sql.next_to(heading, DOWN, buff=0.6)
        self.play(FadeIn(sql, shift=UP * 0.2))
        self.wait(1)

        placeholder_box = SurroundingRectangle(sql[3], color=HL, buff=0.08)
        self.play(Create(placeholder_box))
        self.wait(0.4)

        note = Text(
            "One row per copy — the first three columns pass straight through",
            font_size=22, color=GREY_B,
        )
        note.next_to(sql, DOWN, buff=0.5)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(1.8)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 5 -- Building the view: CASE + EXISTS
# ---------------------------------------------------------------------------

class S05_CaseExists(WatermarkedScene):
    def construct(self):
        heading = Text("Step 2 — compute it with EXISTS", font_size=32,
                        weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        sql = sql_block([
            "CREATE OR REPLACE VIEW copy_view",
            "  (owner, book, copy, available) AS (",
            "  SELECT DISTINCT c.owner, c.book, c.copy,",
            "    CASE",
            "      WHEN EXISTS (",
            "        SELECT * FROM loan l",
            "        WHERE l.owner = c.owner",
            "          AND l.book  = c.book",
            "          AND l.copy  = c.copy",
            "          AND l.returned ISNULL",
            "      ) THEN 'FALSE'",
            "      ELSE 'TRUE'",
            "    END",
            "  FROM copy c",
            ");",
        ], font_size=22, highlight_lines={
            4: ["EXISTS"],
            9: ["ISNULL"],
        })
        sql.next_to(heading, DOWN, buff=0.35)
        self.play(FadeIn(sql))
        self.wait(1.5)

        subquery_box = SurroundingRectangle(
            VGroup(*sql[5:10]), color=HL, buff=0.08,
        )
        subquery_label = Text("a correlated subquery", font_size=22,
                               color=HL)
        subquery_label.next_to(subquery_box, RIGHT, buff=0.35)
        self.play(Create(subquery_box))
        self.play(FadeIn(subquery_label, shift=LEFT * 0.2))
        self.wait(1.4)
        self.play(FadeOut(subquery_box), FadeOut(subquery_label))
        self.play(FadeOut(sql))

        note = Text(
            "l.owner, l.book, l.copy refer back to c — the outer copy row",
            font_size=24, color=ACCENT,
        )
        rule_true = Text(
            "EXISTS ( subquery )  →  TRUE   if the subquery returns at least one row",
            font_size=24, color=ACCENT,
            t2c={"TRUE": HL, "at least one row": HL},
        )
        rule_false = Text(
            "EXISTS ( subquery )  →  FALSE  otherwise — if it returns no rows at all",
            font_size=24, color=ACCENT,
            t2c={"FALSE": HL, "no rows at all": HL},
        )
        notes = VGroup(note, rule_true, rule_false).arrange(DOWN, buff=0.32)
        notes.move_to(ORIGIN)
        self.play(FadeIn(notes, shift=UP * 0.2))
        self.wait(2.6)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 6 -- Walking EXISTS row by row
# ---------------------------------------------------------------------------

class S06_ExistsWalkthrough(WatermarkedScene):
    def construct(self):
        heading = Text("Row by row: does an open loan exist?", font_size=30,
                        weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        copy_group = data_table(COPY_ROWS, COPY_COLS, scale=0.42, name="copy")
        loan_group = data_table(LOAN_ROWS, LOAN_COLS, scale=0.36, name="loan")
        both = VGroup(copy_group, loan_group).arrange(RIGHT, buff=0.7,
                                                        aligned_edge=UP)
        both.next_to(heading, DOWN, buff=0.4)
        colour_returned_column(loan_group)
        self.play(Create(copy_group), Create(loan_group))
        self.wait(0.5)

        copy_table = copy_group[0]
        loan_table = loan_group[0]
        verdict_pos = DOWN * 2.6

        def highlight_copy_row(r):
            return SurroundingRectangle(
                VGroup(*[copy_table.get_entries((r + 2, c))
                         for c in range(1, 4)]),
                color=ACCENT, buff=0.06,
            )

        def highlight_loan_row(r, color):
            return SurroundingRectangle(
                VGroup(*[loan_table.get_entries((r + 2, c))
                         for c in range(1, 7)]),
                color=color, buff=0.06,
            )

        def run_case(copy_idx, exists_true, availability, reason,
                     match_loan_idx=None, reject_loan_idx=None):
            c_box = highlight_copy_row(copy_idx)
            self.play(Create(c_box))
            self.wait(0.3)

            boxes = [c_box]
            if match_loan_idx is not None:
                l_box = highlight_loan_row(match_loan_idx, GOOD)
                self.play(Create(l_box))
                boxes.append(l_box)
            elif reject_loan_idx is not None:
                l_box = highlight_loan_row(reject_loan_idx, BAD)
                self.play(Create(l_box))
                boxes.append(l_box)

            row_count = "returns 1 row" if exists_true else "returns 0 rows"
            exists_str = "TRUE" if exists_true else "FALSE"
            verdict_color = BAD if availability == "FALSE" else GOOD
            verdict_text = Text(
                f"subquery {row_count}  ⇒  EXISTS = {exists_str}"
                f"  ⇒  available = '{availability}'",
                font_size=22, color=verdict_color, weight=BOLD,
            )
            reason_text = Text(reason, font_size=20, color=GREY_B)
            verdict_group = VGroup(verdict_text, reason_text).arrange(
                DOWN, buff=0.12)
            verdict_group.move_to(verdict_pos)
            boxes.append(verdict_group)
            self.play(FadeIn(verdict_group, shift=UP * 0.2))
            self.wait(1.8)

            self.play(*[FadeOut(m) for m in boxes])

        # copy row 0: alice, B1, 1 -- loan row 0 matches AND is open
        run_case(0, True, "FALSE",
                 "loan #1: same owner/book/copy, and returned is NULL",
                 match_loan_idx=0)

        # copy row 1: alice, B2, 1 -- loan row 1 matches but is closed,
        # so it's excluded by "AND l.returned ISNULL" -- 0 rows survive
        run_case(1, False, "TRUE",
                 "loan #2 matches owner/book/copy, but returned isn't NULL — excluded",
                 reject_loan_idx=1)

        # copy row 2: bob, B1, 1 -- no loan row has owner = bob at all,
        # so there's nothing even to check -- 0 rows
        run_case(2, False, "TRUE",
                 "no loan row has owner = bob at all — nothing to check")

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 7 -- The finished view
# ---------------------------------------------------------------------------

class S07_FinalResult(WatermarkedScene):
    def construct(self):
        heading = Text("The view, queried like any table", font_size=32,
                        weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        sql = sql_block(["SELECT * FROM copy_view;"], font_size=28,
                         highlight_lines={0: ["SELECT", "FROM"]})
        sql.next_to(heading, DOWN, buff=0.45)
        self.play(FadeIn(sql, shift=UP * 0.2))
        self.wait(0.8)

        result_cols = ["owner", "book", "copy", "available"]
        result_rows = [
            ["alice", "B1", "1", "FALSE"],
            ["alice", "B2", "1", "TRUE"],
            ["bob", "B1", "1", "TRUE"],
            ["carol", "B3", "1", "FALSE"],
        ]
        result_group = data_table(result_rows, result_cols, scale=0.55,
                                   name="copy_view")
        result_group.next_to(sql, DOWN, buff=0.5)
        self.play(Create(result_group))

        table = result_group[0]
        for r, row in enumerate(result_rows):
            entry = table.get_entries((r + 2, 4))
            entry.set_color(BAD if row[-1] == "FALSE" else GOOD)
        self.wait(2.6)

        self.clear_scene()
