"""
Manim Community animation explaining aggregation in ER diagrams -- built
to accompany BT5110 Tutorial 2 (the VINO tasting-session schema).

Source material: tut_02.tex / tut_02_files/17-21.pdf (the progressive
build-up of the final ER diagram) and the Q2 Logical Design section
(tut_02.tex lines 222-311), which is where `open` and the aggregated
`taste` table come from.

Render all scenes and concatenate them into the final video with:

    bash render.sh

which produces docs/videos/tut_02_er_aggregation.mp4 for the site.
"""

from manim import *

# ---------------------------------------------------------------------------
# Shared styling (mirrors the other two videos for a consistent look)
# ---------------------------------------------------------------------------

ACCENT = "#6fa8dc"
ACCENT_SOFT = "#1b2733"
HL = "#f2c14e"
GOOD = "#89ca78"
BAD = "#e06c75"
MEMBER_FILL = "#2a1f2b"
MONO_FONT = "Menlo"

SQL_KEYWORDS = [
    "SELECT", "DISTINCT", "FROM", "WHERE", "AND",
    "CREATE", "REPLACE", "VIEW", "ALTER", "TABLE", "DROP", "COLUMN",
    "PRIMARY", "KEY", "FOREIGN", "REFERENCES", "NOT", "NULL", "CHECK",
]

config.background_color = "#101114"


def sql_block(lines, font_size=24, highlight_lines=None):
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
    rows.arrange(DOWN, aligned_edge=LEFT, buff=0.14)
    return rows


def labelled_box(mobj, label, color=ACCENT):
    cap = Text(label, font_size=24, color=color, weight=BOLD)
    group = VGroup(cap, mobj).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
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
# ER-diagram building blocks
# ---------------------------------------------------------------------------

def entity_box(label, width=2.3, height=0.9, fill=ACCENT_SOFT, font_size=26):
    box = Rectangle(width=width, height=height, color=WHITE,
                     fill_color=fill, fill_opacity=1, stroke_width=2.5)
    text = Text(label, font_size=font_size, weight=BOLD, color=WHITE)
    text.move_to(box.get_center())
    group = VGroup(box, text)
    group.box = box
    return group


def rel_diamond(label, width=1.9, height=1.0, font_size=21, color=WHITE):
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


def card_label(text, mobj, direction=UP, buff=0.1, font_size=18,
               color=GREY_B):
    t = Text(text, font_size=font_size, color=color)
    t.next_to(mobj, direction, buff=buff)
    return t


# ---------------------------------------------------------------------------
# Attribute-connector building blocks (Merise-style circles: hollow = plain
# attribute, filled = identifying attribute; a filled circle joined by a
# bar means "these together form a composite key")
# ---------------------------------------------------------------------------

DOT_R = 0.05


def filled_dot(point):
    return Dot(point, radius=DOT_R, color=WHITE)


def hollow_dot(point):
    return Circle(radius=DOT_R, color=WHITE, stroke_width=2,
                   fill_color=config.background_color, fill_opacity=1
                   ).move_to(point)


def composite_attrs(entity, labels, x_offsets, direction=DOWN,
                     key_gap=0.4, leaf_gap=0.4, font_size=15):
    """A composite-key group: entity -> filled circle (joined by a bar)
    -> hollow circle -> label, one branch per offset in x_offsets."""
    base = entity.get_bottom() if direction is DOWN else entity.get_top()
    sign = -1 if direction is DOWN else 1
    group = VGroup()
    key_pts = []
    for dx in x_offsets:
        top_pt = base + RIGHT * dx
        key_pt = top_pt + UP * sign * key_gap
        group.add(Line(top_pt, key_pt, color=WHITE, stroke_width=2))
        key_pts.append(key_pt)
    group.add(Line(key_pts[0], key_pts[-1], color=WHITE, stroke_width=2))
    for pt in key_pts:
        group.add(filled_dot(pt))
    for pt, label in zip(key_pts, labels):
        leaf_pt = pt + UP * sign * leaf_gap
        group.add(Line(pt, leaf_pt, color=WHITE, stroke_width=2))
        group.add(hollow_dot(leaf_pt))
        txt = Text(label, font_size=font_size, color=GREY_B)
        txt.next_to(leaf_pt, direction, buff=0.08)
        group.add(txt)
    return group


def simple_attrs(entity, specs, direction=DOWN, gap=0.55, font_size=15):
    """specs: list of (x_offset, label, filled:bool). Independent
    (non-composite) attribute branches, straight from the entity."""
    base = entity.get_bottom() if direction is DOWN else entity.get_top()
    sign = -1 if direction is DOWN else 1
    group = VGroup()
    for dx, label, filled in specs:
        top_pt = base + RIGHT * dx
        end_pt = top_pt + UP * sign * gap
        group.add(Line(top_pt, end_pt, color=WHITE, stroke_width=2))
        dot = filled_dot(end_pt) if filled else hollow_dot(end_pt)
        group.add(dot)
        txt = Text(label, font_size=font_size, color=GREY_B)
        txt.next_to(end_pt, direction, buff=0.08)
        group.add(txt)
    return group


# ---------------------------------------------------------------------------
# Scene 1 -- Title
# ---------------------------------------------------------------------------

class S01_Title(WatermarkedScene):
    def construct(self):
        kicker = Text("BT5110 · Tutorial 2", font_size=28, color=ACCENT)
        title = Text("Aggregation in ER Diagrams", font_size=52, weight=BOLD)
        sub = Text(
            "Wiring one relationship into another",
            font_size=26, color=GREY_B,
        )
        group = VGroup(kicker, title, sub).arrange(DOWN, buff=0.35)
        self.play(FadeIn(kicker, shift=UP * 0.2))
        self.play(Write(title))
        self.play(FadeIn(sub, shift=UP * 0.2))
        self.wait(1.2)
        self.play(FadeOut(group))


# ---------------------------------------------------------------------------
# Scene 2 -- Relationships are verbs
# ---------------------------------------------------------------------------

class S02_RelationshipsAreVerbs(WatermarkedScene):
    def construct(self):
        heading = Text("A relationship is a verb", font_size=34, weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        session = entity_box("session")
        opened = rel_diamond("opened")
        bottle = entity_box("bottle")
        row1 = VGroup(session, opened, bottle).arrange(RIGHT, buff=1.0)
        row1.move_to(UP * 1.3)
        l1a = hline(session, opened)
        l1b = hline(opened, bottle)

        self.play(FadeIn(session), FadeIn(bottle))
        self.play(Create(l1a), Create(l1b), FadeIn(opened))
        cap1 = Text("a session opens a bottle", font_size=24, color=ACCENT)
        cap1.next_to(row1, DOWN, buff=0.35)
        self.play(FadeIn(cap1, shift=UP * 0.2))
        self.wait(1.4)

        member = entity_box("member", fill=MEMBER_FILL)
        tasted = rel_diamond("tasted")
        bottle2 = entity_box("bottle")
        row2 = VGroup(member, tasted, bottle2).arrange(RIGHT, buff=1.0)
        row2.move_to(DOWN * 1.3)
        l2a = hline(member, tasted)
        l2b = hline(tasted, bottle2)

        self.play(FadeIn(member), FadeIn(bottle2))
        self.play(Create(l2a), Create(l2b), FadeIn(tasted))
        cap2 = Text("a member tastes a bottle", font_size=24, color=ACCENT)
        cap2.next_to(row2, DOWN, buff=0.35)
        self.play(FadeIn(cap2, shift=UP * 0.2))
        self.wait(1.6)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 3 -- The constraint the simple design misses
# ---------------------------------------------------------------------------

class S03_MissingConstraint(WatermarkedScene):
    def construct(self):
        heading = Text("A constraint this misses", font_size=34,
                        weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        b1 = Text("A tasting session happens at most once a week.",
                   font_size=26, color=WHITE)
        b2 = Text(
            "Every bottle opened in a session is finished in that\n"
            "session — a bottle is opened exactly once, ever.",
            font_size=26, color=WHITE, line_spacing=1.3,
        )
        bullets = VGroup(b1, b2).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        bullets.next_to(heading, DOWN, buff=0.7)
        self.play(FadeIn(b1, shift=UP * 0.2))
        self.wait(0.8)
        self.play(FadeIn(b2, shift=UP * 0.2))
        self.wait(1.2)

        conclusion = Text(
            "So a rating belongs to a specific opening event —\n"
            "not to a bottle sitting in the cellar.",
            font_size=27, color=HL, weight=BOLD, line_spacing=1.3,
        )
        conclusion.next_to(bullets, DOWN, buff=0.7)
        self.play(FadeIn(conclusion, shift=UP * 0.2))
        self.wait(2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 4 -- Can a verb plug into another verb?
# ---------------------------------------------------------------------------

class S04_CantWireVerbToVerb(WatermarkedScene):
    def construct(self):
        heading = Text("Can tasted just point at opened?", font_size=32,
                        weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        session = entity_box("session", width=2.0, height=0.8, font_size=22)
        opened = rel_diamond("opened", width=1.7, height=0.9, font_size=20)
        bottle = entity_box("bottle", width=2.0, height=0.8, font_size=22)
        top_row = VGroup(session, opened, bottle).arrange(RIGHT, buff=0.8)
        top_row.next_to(heading, DOWN, buff=0.7)
        self.play(FadeIn(top_row))
        self.play(Create(hline(session, opened)),
                   Create(hline(opened, bottle)))

        member = entity_box("member", width=2.0, height=0.8, font_size=22,
                             fill=MEMBER_FILL)
        tasted = rel_diamond("tasted", width=1.7, height=0.9, font_size=20)
        bottom_row = VGroup(member, tasted).arrange(RIGHT, buff=0.8)
        bottom_row.next_to(top_row, DOWN, buff=1.3).align_to(top_row, LEFT)
        self.play(FadeIn(bottom_row))
        self.play(Create(hline(member, tasted)))
        self.wait(0.5)

        bad_line = DashedLine(
            tasted.get_top(), opened.get_bottom(), color=BAD, stroke_width=3,
        )
        cross = Text("✗", font_size=34, color=BAD, weight=BOLD)
        cross.move_to(bad_line.get_center())
        self.play(Create(bad_line))
        self.play(FadeIn(cross, scale=1.4))
        self.wait(0.8)

        note = Text(
            "A relationship (diamond) can only connect to entities\n"
            "(rectangles) — never straight to another relationship.",
            font_size=24, color=BAD, line_spacing=1.3,
        )
        note.next_to(bottom_row, DOWN, buff=0.7)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(2.2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 5 -- The fix: aggregation
# ---------------------------------------------------------------------------

class S05_Aggregation(WatermarkedScene):
    def construct(self):
        heading = Text("Aggregation: turn the fact into an entity",
                        font_size=30, weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        session = entity_box("session", width=2.0, height=0.8, font_size=22)
        opened = rel_diamond("opened", width=1.7, height=0.9, font_size=20)
        bottle = entity_box("bottle", width=2.0, height=0.8, font_size=22)
        top_row = VGroup(session, opened, bottle).arrange(RIGHT, buff=0.8)
        top_row.next_to(heading, DOWN, buff=0.65)
        self.play(FadeIn(top_row))
        self.play(Create(hline(session, opened)),
                   Create(hline(opened, bottle)))
        self.wait(0.6)

        agg_box = SurroundingRectangle(opened, color=HL, buff=0.4,
                                        corner_radius=0.1, stroke_width=3)
        self.play(Create(agg_box))
        self.wait(0.4)

        note1 = Text(
            "The diamond is the verb. The rectangle around it is the",
            font_size=23, color=HL,
        )
        note2 = Text(
            "fact that verb creates — as if it were a brand-new entity.",
            font_size=23, color=HL,
        )
        notes = VGroup(note1, note2).arrange(DOWN, buff=0.12)
        notes.next_to(agg_box, DOWN, buff=0.35)
        self.play(FadeIn(notes, shift=UP * 0.2))
        self.wait(1.8)
        self.play(FadeOut(notes))

        member = entity_box("member", width=2.0, height=0.8, font_size=22,
                             fill=MEMBER_FILL)
        tasted = rel_diamond("tasted", width=1.7, height=0.9, font_size=20)
        bottom = VGroup(member, tasted).arrange(RIGHT, buff=0.8)
        bottom.next_to(agg_box, DOWN, buff=1.1)
        tasted.move_to(bottom[1])
        member.move_to(bottom[0])
        self.play(FadeIn(bottom))
        self.play(Create(hline(member, tasted)))
        connector = vline(agg_box, tasted, color=GOOD, stroke_width=3)
        self.play(Create(connector))
        self.wait(0.4)

        note3 = Text(
            "Now tasted legally connects two entities again:",
            font_size=23, color=GOOD,
        )
        note4 = Text(
            "member, and the aggregate  ⟨ session–opened–bottle ⟩",
            font_size=23, color=GOOD,
        )
        notes2 = VGroup(note3, note4).arrange(DOWN, buff=0.12)
        notes2.next_to(bottom, DOWN, buff=0.5)
        self.play(FadeIn(notes2, shift=UP * 0.2))
        self.wait(2.2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 6 -- The full VINO diagram
# ---------------------------------------------------------------------------

class S06_FullDiagram(WatermarkedScene):
    def construct(self):
        heading = Text("The full VINO diagram", font_size=30, weight=BOLD)
        heading.to_edge(UP, buff=0.3)
        self.play(FadeIn(heading, shift=UP * 0.2))

        ew, eh, ef = 1.7, 0.62, 17
        dw, dh, df = 1.4, 0.7, 16

        # Top row: session -- opened -- bottle
        session = entity_box("session", width=ew, height=eh, font_size=ef)
        opened = rel_diamond("opened", width=dw, height=dh, font_size=df)
        bottle = entity_box("bottle", width=ew, height=eh, font_size=ef)
        top = VGroup(session, opened, bottle).arrange(RIGHT, buff=1.0)
        top.move_to(UP * 1.25 + LEFT * 1.35)

        # Right column: bottle -- contain -- wine
        contain = rel_diamond("contain", width=dw, height=dh, font_size=df)
        wine = entity_box("wine", width=2.7, height=eh, font_size=ef)
        contain.next_to(bottle, DOWN, buff=0.62)
        wine.next_to(contain, DOWN, buff=0.62)

        # Left column: opened -- tasted -- member
        tasted = rel_diamond("tasted", width=dw, height=dh, font_size=df)
        member = entity_box("member", width=ew, height=eh, font_size=ef,
                             fill=MEMBER_FILL)
        tasted.next_to(opened, DOWN, buff=0.62)
        member.next_to(tasted, DOWN, buff=0.62)

        diagram = VGroup(session, opened, bottle, contain, wine, tasted,
                          member)

        # Aggregate box floats around "opened" alone -- not touching it --
        # session/bottle's wires cross into it to reach the diamond, but
        # tasted (the relationship built on top of the aggregate) connects
        # to the box itself, not to the diamond inside it.
        agg_box = SurroundingRectangle(opened, color=HL, buff=0.3,
                                        corner_radius=0.08, stroke_width=2.5)

        lines = VGroup(
            hline(session, opened), hline(opened, bottle),
            vline(bottle, contain), vline(contain, wine),
            vline(agg_box, tasted), vline(tasted, member),
        )

        self.play(FadeIn(session), FadeIn(bottle), FadeIn(wine),
                   FadeIn(member))
        self.play(Create(lines[0]), Create(lines[1]), FadeIn(opened))
        self.play(Create(lines[2]), Create(lines[3]), FadeIn(contain))
        self.wait(0.5)

        self.play(Create(agg_box))
        self.wait(0.4)

        self.play(Create(lines[4]), Create(lines[5]), FadeIn(tasted))
        self.wait(0.6)

        c1 = card_label("(0,n)", lines[0], UP, font_size=16)
        c2 = card_label("(0,1)", lines[1], UP, font_size=16)
        c3 = card_label("(1,1)", lines[2], RIGHT, buff=0.12, font_size=16)
        c4 = card_label("(0,n)", lines[3], RIGHT, buff=0.12, font_size=16)
        c5 = card_label("(1,n)", lines[4], LEFT, buff=0.12, font_size=16)
        c6 = card_label("(0,n)", lines[5], LEFT, buff=0.12, font_size=16)
        cards = VGroup(c1, c2, c3, c4, c5, c6)
        self.play(FadeIn(cards))
        self.wait(0.6)

        # ---- attributes ----
        attrs = VGroup()

        # session: year, week (composite key)
        attrs.add(composite_attrs(session, ["year", "week"], [-0.42, 0.42]))

        # bottle: in_cellar (derived, dashed), Number (weak-entity key)
        cellar_top = bottle.get_top() + LEFT * 0.42
        cellar_end = cellar_top + UP * 0.5
        attrs.add(DashedLine(cellar_top, cellar_end, color=WHITE,
                              stroke_width=2, dash_length=0.05))
        attrs.add(hollow_dot(cellar_end))
        cellar_label = Text("in_cellar", font_size=15, color=GREY_B)
        cellar_label.next_to(cellar_end, UP, buff=0.08)
        attrs.add(cellar_label)

        num_top = bottle.get_top() + RIGHT * 0.42
        num_junction = num_top + UP * 0.32
        num_leaf = num_junction + UP * 0.32
        attrs.add(Line(num_top, num_junction, color=WHITE, stroke_width=2))
        attrs.add(filled_dot(num_junction))
        attrs.add(Line(num_junction, num_leaf, color=WHITE, stroke_width=2))
        attrs.add(hollow_dot(num_leaf))
        num_label = Text("Number", font_size=15, color=GREY_B)
        num_label.next_to(num_leaf, UP, buff=0.08)
        attrs.add(num_label)

        # Number is scoped by wine (weak entity): route right, down, then
        # into the same point where contain's wire meets wine, raised
        # slightly off the box edge.
        wine_junction = wine.get_top() + UP * 0.15
        route = VMobject(color=WHITE, stroke_width=2)
        via = num_junction + RIGHT * 1.15
        route.set_points_as_corners([
            num_junction, via, np.array([via[0], wine_junction[1], 0]),
            wine_junction,
        ])
        attrs.add(route)
        attrs.add(filled_dot(wine_junction))

        # wine: Others (plain), W.Name / Appellation / Vintage (composite)
        others_top = wine.get_top() + LEFT * 0.75
        others_end = others_top + UP * 0.5
        attrs.add(Line(others_top, others_end, color=WHITE, stroke_width=2))
        attrs.add(hollow_dot(others_end))
        others_label = Text("Others", font_size=15, color=GREY_B)
        others_label.next_to(others_end, UP, buff=0.08)
        attrs.add(others_label)

        attrs.add(composite_attrs(
            wine, ["W.Name", "Appellation", "Vintage"], [-1.0, 0, 1.0]))

        # member: Name, Address (plain), C.id (identifier)
        attrs.add(simple_attrs(member, [
            (-0.85, "Name", False),
            (0, "Address", False),
            (0.85, "C.id", True),
        ]))

        # tasted: Rating (plain, diagonal to the lower-left) -- attach to
        # a point on the diamond's actual lower-left edge, not the empty
        # corner of its bounding box.
        rating_top = (tasted.diamond.get_left() +
                      tasted.diamond.get_bottom()) / 2
        rating_end = rating_top + LEFT * 0.55 + DOWN * 0.2
        attrs.add(Line(rating_top, rating_end, color=WHITE, stroke_width=2))
        attrs.add(hollow_dot(rating_end))
        rating_label = Text("Rating", font_size=15, color=GREY_B)
        rating_label.next_to(rating_end, LEFT, buff=0.08)
        attrs.add(rating_label)

        self.play(FadeIn(attrs))
        self.wait(2.2)

        self.clear_scene()


# ---------------------------------------------------------------------------
# Scene 7 -- From ER to relational schema
# ---------------------------------------------------------------------------

class S07_ToRelational(WatermarkedScene):
    def construct(self):
        heading = Text("From aggregate to foreign key", font_size=32,
                        weight=BOLD)
        heading.to_edge(UP)
        self.play(FadeIn(heading, shift=UP * 0.2))

        open_sql = sql_block([
            "CREATE TABLE open (",
            "  bottle_number INTEGER,",
            "  session_year  INTEGER,",
            "  PRIMARY KEY (bottle_number, ...)",
            ");",
        ], font_size=21, highlight_lines={0: ["CREATE", "TABLE"],
                                           3: ["PRIMARY", "KEY"]})
        open_panel = labelled_box(open_sql, "opened  →  open")

        taste_sql = sql_block([
            "CREATE TABLE taste (",
            "  member CHAR(10),",
            "  bottle_number INTEGER,",
            "  rating VARCHAR(32),",
            "  FOREIGN KEY (bottle_number, ...)",
            "    REFERENCES open (...)",
            ");",
        ], font_size=21, highlight_lines={5: ["REFERENCES"]})
        taste_panel = labelled_box(taste_sql, "tasted  →  taste")

        panels = VGroup(open_panel, taste_panel).arrange(
            RIGHT, buff=1.0, aligned_edge=UP)
        panels.next_to(heading, DOWN, buff=0.5)

        self.play(FadeIn(open_panel, shift=RIGHT * 0.2))
        self.wait(1)
        self.play(FadeIn(taste_panel, shift=LEFT * 0.2))
        self.wait(1.2)

        ref_line = taste_sql[5]
        ref_box = Underline(ref_line, color=HL, buff=0.05, stroke_width=3)
        self.play(Create(ref_box))
        self.wait(0.6)

        note = Text(
            "taste references open, not bottle — a rating is tied to a",
            font_size=23, color=HL,
        )
        note2 = Text(
            "specific opening event, exactly what the aggregation encodes",
            font_size=23, color=HL,
        )
        notes = VGroup(note, note2).arrange(DOWN, buff=0.12)
        notes.next_to(VGroup(open_panel, taste_panel), DOWN, buff=0.8)
        self.play(FadeIn(notes, shift=UP * 0.2))
        self.wait(2.6)

        self.clear_scene()
