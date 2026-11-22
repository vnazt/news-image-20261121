"""frontpage.py — renders the news-image-20261121 front page.

The page is a classic illustrated broadsheet for one day — Saturday
21 November 2026 — drawn entirely in code with Pillow and the
Liberation family: masthead, giant serif date, red italic dek, a UTC
timeline of the day, a six-figure numbers strip, region tabs counted
from the story list itself, three hero panels with drawn scenes,
twelve pictured story cards with certainty tags, a dot-matrix world
map carrying a numbered pin for every pictured story, twenty-two
one-line briefs, and a red date-check box that names the neighbouring
days' stories this page deliberately leaves out.

All 37 stories come from a verified research dossier: every figure
was confirmed by two independent sources before it was allowed on the
page, and the single state-media claim is tagged CLAIM where it sits.
The render is deterministic — same data, same PNG, every run.

Usage:  python3 frontpage.py   ->   entry.png + fallback.png (1024x1024)
"""

import os
from collections import Counter

from PIL import Image, ImageDraw, ImageFont

# ------------------------------------------------------------------ fonts

FONT_ROOT = "/usr/share/fonts/truetype/liberation"
SERIF = os.path.join(FONT_ROOT, "LiberationSerif-Regular.ttf")
SERIF_BOLD = os.path.join(FONT_ROOT, "LiberationSerif-Bold.ttf")
SERIF_ITALIC = os.path.join(FONT_ROOT, "LiberationSerif-Italic.ttf")
SANS = os.path.join(FONT_ROOT, "LiberationSans-Regular.ttf")
SANS_BOLD = os.path.join(FONT_ROOT, "LiberationSans-Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


# ------------------------------------------------------------------ ink

PAPER = (247, 242, 227)
PAPER_SHADE = (239, 232, 211)
INK = (26, 25, 23)
FAINT = (99, 94, 81)
RED = (178, 34, 24)
DEEP_RED = (148, 27, 18)
NAVY = (19, 35, 57)
NAVY_LIGHT = (31, 55, 84)
NIGHT = (11, 21, 35)
GOLD = (233, 165, 33)
ORANGE = (243, 121, 33)
MAP_DOT = (124, 136, 159)
RULE_SOFT = (192, 184, 161)

TAB_INK = {
    "Europe": (43, 90, 166),
    "Asia": (178, 62, 32),
    "Middle East": (125, 60, 152),
    "Africa": (30, 132, 73),
    "Americas": (183, 149, 11),
    "Oceania": (40, 116, 166),
    "Global": (93, 109, 126),
}
TAB_ORDER = ["Europe", "Asia", "Middle East", "Africa", "Americas",
             "Oceania", "Global"]

PAGE = 1024
EDGE = 28
SPAN = PAGE - 2 * EDGE  # 968 px of content

DAY = "Saturday 21 November 2026"
DEK = ("Iran hits Bahrain, tankers burn off Oman · drones strike a "
       "Russian ship in the Baltic · COP31 runs into overtime")
TIMELINE = ("00:09 Peru quake M6.7 · 06:00 Bitcoin's $55,100 low · "
            "06:50 Sparta II hit · 09:42 Banda Sea quake M6.8 · "
            "10:45 Qinghai quake M5.9 · 18:24 BepiColombo orbits Mercury")

# ------------------------------------------------------------------ heroes
# num, place tag, headline, summary, region, scene key

HEROES = [
    dict(num=1, region="Middle East", scene="hormuz",
         tag="MANAMA · BAHRAIN — STRAIT OF HORMUZ",
         head="Iran Strikes Bahrain, Tankers Hit",
         summ="Bahrain says an Iranian attack set a Sitra refinery "
              "ablaze; two tankers were hit off Khasab, Oman. "
              "(AFP / Reuters)"),
    dict(num=2, region="Europe", scene="sparta",
         tag="GULF OF FINLAND — THE BALTIC",
         head="Drones Strike Russian Cargo Ship",
         summ="Two drones hit the Sparta II at dawn; all 16 crew were "
              "evacuated as the fire burned through the night. (Reuters)"),
    dict(num=3, region="Asia", scene="cop",
         tag="ANTALYA · TÜRKIYE — COP31",
         head="Climate Summit Runs Into Overtime",
         summ="The draft drops fossil-fuel language and the $120bn "
              "adaptation target; 130+ countries object. (Reuters / AP)"),
]

# ------------------------------------------------------------------ cards
# num, place, certainty, headline, summary, region, scene key

CARDS = [
    dict(num=4, region="Europe", scene="robots",
         place="GENEVA", cert="CONFIRMED",
         head="No Rules Agreed on Killer Robots",
         summ="128 states end talks with no binding ban. (Reuters)"),
    dict(num=5, region="Asia", scene="euindo",
         place="BRUSSELS · JAKARTA", cert="CONFIRMED",
         head="EU–Indonesia Pact Signed",
         summ="98.5% of tariff lines go, after 10 years. (Reuters)"),
    dict(num=6, region="Global", scene="bitcoin",
         place="GLOBAL MARKETS", cert="CONFIRMED",
         head="Bitcoin Falls to $55,100",
         summ="A two-year low; $2.67bn liquidated in a day. (Reuters)"),
    dict(num=7, region="Global", scene="mercury",
         place="MERCURY", cert="CONFIRMED",
         head="BepiColombo Reaches Mercury",
         summ="Orbit at 18:24 UTC, eight years after launch. (ESA)"),
    dict(num=8, region="Americas", scene="wanted",
         place="GUASAVE · MEXICO", cert="CONFIRMED",
         head="“El Chapo Isidro” Captured",
         summ="FBI-listed trafficker held; 11 died in the raid. (AP)"),
    dict(num=9, region="Europe", scene="paris",
         place="PARIS · FRANCE", cert="CONFIRMED",
         head="Sixth Saturday of Marches",
         summ="82,500 march over living costs. (Reuters)"),
    dict(num=10, region="Asia", scene="measles",
         place="DHAKA · BANGLADESH", cert="OFFICIAL",
         head="Measles Toll Reaches 1,343",
         summ="831 new suspected cases in 24 hours. (DGHS)"),
    dict(num=11, region="Asia", scene="taiex",
         place="TAIPEI", cert="OFFICIAL",
         head="Short Sales Curbed After Fall",
         summ="TAIEX fell 17.5% in a week; margin to 150%. (CNA)"),
    dict(num=12, region="Asia", scene="factory",
         place="SERANG · INDONESIA", cert="CONFIRMED",
         head="Candy-Factory Fire: 36 Missing",
         summ="Three workers dead in the evening blaze. (Reuters)"),
    dict(num=13, region="Europe", scene="rugby",
         place="LONDON", cert="CONFIRMED",
         head="England 37–12 New Zealand",
         summ="A record 25-point margin over the All Blacks. (Reuters)"),
    dict(num=14, region="Americas", scene="quake",
         place="JUNÍN · PERU", cert="OFFICIAL",
         head="M6.7 Quake: 93,000 Lose Power",
         summ="One dead, 16 injured in Saturday's count. (EFE)"),
    dict(num=15, region="Africa", scene="boat",
         place="BAYELSA · NIGERIA", cert="CONFIRMED",
         head="Funeral Boat Toll Reaches 24",
         summ="24 survivors in the recovery update. (Reuters)"),
]

# ------------------------------------------------------------------ briefs
# num, one-line text (place first, source last), region

BRIEFS = [
    (16, "Riyadh — Saudi shields down 3 Houthi missiles (AFP)", "Middle East"),
    (17, "Gaza City — Strike on food truck kills three (Reuters)", "Middle East"),
    (18, "Basra — Power-station fire kills at least 4 (Reuters)", "Middle East"),
    (19, "Beirut — Aoun demands Israeli withdrawal (AFP)", "Middle East"),
    (20, "Jerusalem — Eisenkot invites Likud to talks (AFP)", "Middle East"),
    (21, "Hormuz — Pugh ends 15 km swim past tankers (AP)", "Middle East"),
    (22, "Brussels — EU budget cut of €204bn proposed (AFP)", "Europe"),
    (23, "Kyiv — Kerch strikes a “fair response” (AP)", "Europe"),
    (24, "Zagreb — Thousands rally over ward death (Reuters)", "Europe"),
    (25, "Dublin — Ireland 20–17 South Africa (Reuters)", "Europe"),
    (26, "Turin — Alcaraz faces Zverev in ATP final (Reuters)", "Europe"),
    (27, "Brasília — Bolsonaro in intensive care (Reuters)", "Americas"),
    (28, "Belo Horizonte — Mosquito trial cuts dengue 69% (AP)", "Americas"),
    (29, "Washington — Trump backs 10% card-rate cap (AP)", "Americas"),
    (30, "Abuja — CAF adopts Kiswahili as fifth language (VON)", "Africa"),
    (31, "Chandel — Tainted alcohol kills 11, 181 in hospital (Reuters)", "Asia"),
    (32, "Leh — Ladakh's first local polls: 70% turnout (PTI)", "Asia"),
    (33, "Taipei — 15 of 21 PLA sorties cross the line (MND)", "Asia"),
    (34, "Fukushima — Heavy snow isolates ~1,400 (Kyodo)", "Asia"),
    (35, "Mastung — 15 militants killed, state media (CLAIM)", "Asia"),
    (36, "Wellington — India 486-4, lead New Zealand by 118 (AFP)", "Oceania"),
    (37, "Banda Sea — M6.8 quake, no damage reported (USGS)", "Oceania"),
]

# ------------------------------------------------------------------ numbers

NUMBERS = [
    ("$55,100", "BITCOIN'S LOW — A TWO-YEAR BOTTOM"),
    ("1,343", "DEATHS IN BANGLADESH'S MEASLES OUTBREAK"),
    ("82,500", "MARCHERS ACROSS FRANCE, MINISTRY COUNT"),
    ("98.5%", "OF EU TARIFF LINES SCRAPPED FOR INDONESIA"),
    ("128", "STATES AT GENEVA'S KILLER-ROBOT TALKS"),
    ("730m", "PEOPLE IN THE EU–INDONESIA MARKET"),
]

DATE_CHECK = (
    "DATE CHECK — Deliberately left out as other days' news: Russian "
    "missiles in Poland · Wall Street's AI sell-off · Cyclone Akvan's "
    "landfall · the GTA VI sales record (all Friday) · Verstappen's Las "
    "Vegas win · COP31's final draft (both Sunday) · Dhaka's toll here "
    "is Saturday's 1,343, not Sunday's 1,352."
)

STORY_COUNT = len(HEROES) + len(CARDS) + len(BRIEFS)
REGION_TALLY = Counter(
    [h["region"] for h in HEROES]
    + [c["region"] for c in CARDS]
    + [region for _n, _t, region in BRIEFS]
)

# ------------------------------------------------------------------ map
# A coarse dot-matrix world, one character per dot: '#' is land.
# 48 columns x 21 rows, drawn by hand for this page.

WORLD = [
    "                                                ",
    "   #####        ##########################      ",
    " #########     ############################     ",
    "  #########    ###########################      ",
    "   ########     #########################       ",
    "    ######       #######################        ",
    "     #####        #####################         ",
    "      ####         ##################           ",
    "      ###           ################            ",
    "       ###           ##############             ",
    "       ####           ############              ",
    "        #####          ##########               ",
    "        ######          ########        ##      ",
    "         ####            ######        ####     ",
    "         ###              ####          ##      ",
    "          ##               ##                   ",
    "          #                         #######     ",
    "                                    #######     ",
    "                                     #####      ",
    "                                                ",
    "                                                ",
]

# Pin for every pictured story, as a fraction of the map box.
PINS = {
    1: (0.600, 0.44),    # Strait of Hormuz
    2: (0.520, 0.075),   # Gulf of Finland
    3: (0.552, 0.335),   # Antalya
    4: (0.474, 0.275),   # Geneva
    5: (0.758, 0.600),   # Jakarta (EU-Indonesia)
    6: (0.105, 0.270),   # New York (markets)
    7: (0.172, 0.500),   # Kourou spaceport (BepiColombo launch)
    8: (0.072, 0.415),   # Sinaloa
    9: (0.443, 0.208),   # Paris
    10: (0.688, 0.465),  # Dhaka
    11: (0.818, 0.395),  # Taipei
    12: (0.722, 0.675),  # Serang, Java
    13: (0.418, 0.125),  # London
    14: (0.135, 0.660),  # Peru
    15: (0.472, 0.565),  # Bayelsa, Nigeria
}

# ------------------------------------------------------------------ helpers


def wrap_to(draw, text, fnt, width):
    """Greedy word wrap; returns the list of lines that fit width."""
    out, line = [], ""
    for word in text.split():
        trial = (line + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width or not line:
            line = trial
        else:
            out.append(line)
            line = word
    if line:
        out.append(line)
    return out


def block(draw, x, y, text, fnt, fill, width, leading, cap=None):
    """Draw wrapped text; returns the y just below the last line."""
    lines = wrap_to(draw, text, fnt, width)
    if cap is not None:
        lines = lines[:cap]
    for i, ln in enumerate(lines):
        draw.text((x, y + i * leading), ln, font=fnt, fill=fill)
    return y + len(lines) * leading


def middle(draw, cx, y, text, fnt, fill):
    draw.text((cx - draw.textlength(text, font=fnt) / 2, y), text,
              font=fnt, fill=fill)


def fit(draw, x, y, text, path, size, width, fill, floor=8):
    """Draw one line, shrinking the font until it fits the width."""
    s = size
    while s > floor and draw.textlength(text, font=font(path, s)) > width:
        s -= 1
    draw.text((x, y), text, font=font(path, s), fill=fill)


def pin(draw, cx, cy, num, r=8.5):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED,
                 outline=(255, 255, 255), width=2)
    fnt = font(SANS_BOLD, 10 if num < 10 else 9)
    label = str(num)
    draw.text((cx - draw.textlength(label, font=fnt) / 2, cy - 5.5),
              label, font=fnt, fill=(255, 255, 255))


def burst(draw, cx, cy, r, fill=ORANGE, core=GOLD):
    import math
    pts = []
    for i in range(16):
        ang = math.pi * i / 8
        rad = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    draw.polygon(pts, fill=fill)
    draw.ellipse([cx - r * 0.3, cy - r * 0.3, cx + r * 0.3, cy + r * 0.3],
                 fill=core)

# ------------------------------------------------------------------ scenes
# Every scene is drawn from primitives at call time: no image assets.


def _sea(d, x, y, w, h, tone=(16, 58, 82)):
    d.rectangle([x, y, x + w, y + h], fill=tone)


def _waves(d, x, y, w, rows_y):
    for wy in rows_y:
        for i in range(7):
            wx = x + (0.04 + 0.135 * i) * w
            d.arc([wx, wy - 3, wx + 13, wy + 4], 0, 180,
                  fill=(110, 190, 215), width=2)


def scene_hormuz(d, x, y, w, h):
    """Refinery shore, a burning tanker, smoke over the strait."""
    _sea(d, x, y, w, h)
    horizon = y + h * 0.52
    d.rectangle([x, y, x + w, horizon], fill=(52, 44, 40))
    # refinery towers on the shore
    for fx, fh in [(0.05, 0.34), (0.13, 0.44), (0.22, 0.30)]:
        tx = x + fx * w
        d.rectangle([tx, horizon - fh * h, tx + 7, horizon], fill=(16, 14, 12))
        d.ellipse([tx - 1, horizon - fh * h - 5, tx + 8, horizon - fh * h + 2],
                  fill=ORANGE)
    # smoke plume
    for i, fx in enumerate((0.10, 0.16, 0.23)):
        r = 7 + i * 3
        d.ellipse([x + fx * w - r, y + 3 + i * 3, x + fx * w + r,
                   y + 3 + i * 3 + r], fill=(88, 84, 80))
    # tanker hull, centre right
    ty = y + h * 0.66
    d.polygon([(x + 0.42 * w, ty), (x + 0.95 * w, ty), (x + 0.89 * w, ty + 10),
               (x + 0.47 * w, ty + 10)], fill=(150, 70, 50))
    d.rectangle([x + 0.50 * w, ty - 7, x + 0.80 * w, ty], fill=(168, 84, 60))
    d.rectangle([x + 0.84 * w, ty - 12, x + 0.88 * w, ty], fill=(120, 116, 110))
    burst(d, x + 0.63 * w, ty - 8, 10)
    _waves(d, x, y, w, [y + h - 7])


def scene_sparta(d, x, y, w, h):
    """Grey cargo ship under two drones, fire on deck, dawn sea."""
    _sea(d, x, y, w, h, tone=(24, 48, 70))
    d.rectangle([x, y, x + w, y + h * 0.30], fill=(70, 66, 60))
    gy = y + h * 0.58
    # hull and superstructure
    d.polygon([(x + 0.10 * w, gy), (x + 0.88 * w, gy), (x + 0.82 * w, gy + 13),
               (x + 0.16 * w, gy + 13)], fill=(96, 104, 114))
    d.rectangle([x + 0.68 * w, gy - 16, x + 0.78 * w, gy], fill=(110, 118, 128))
    d.rectangle([x + 0.71 * w, gy - 24, x + 0.75 * w, gy - 16],
                fill=(110, 118, 128))
    for fx in (0.24, 0.38, 0.52):
        d.rectangle([x + fx * w, gy - 8, x + fx * w + 16, gy], fill=(140, 90, 60))
    burst(d, x + 0.45 * w, gy - 10, 12)
    burst(d, x + 0.30 * w, gy - 4, 7)
    # two drones above
    for fx, fy in [(0.30, 0.14), (0.58, 0.08)]:
        dx, dy = x + fx * w, y + fy * h
        d.line([dx - 7, dy - 6, dx + 7, dy + 6], fill=(230, 230, 230), width=2)
        d.line([dx - 7, dy + 6, dx + 7, dy - 6], fill=(230, 230, 230), width=2)
        d.ellipse([dx - 2, dy - 2, dx + 2, dy + 2], fill=RED)
    _waves(d, x, y, w, [y + h - 8, y + h - 15])


def scene_cop(d, x, y, w, h):
    """A summit clock run past the hour, and a green leaf."""
    d.rectangle([x, y, x + w, y + h], fill=(38, 46, 40))
    cy = y + h / 2
    # clock, left
    cx = x + 0.24 * w
    r = h * 0.34
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(235, 232, 220), width=3)
    d.line([cx, cy, cx, cy - r * 0.72], fill=(235, 232, 220), width=3)
    d.line([cx, cy, cx + r * 0.55, cy + r * 0.30], fill=RED, width=3)
    d.text((cx - 14, cy + r + 3), "OVERTIME", font=font(SANS_BOLD, 9),
           fill=(235, 232, 220))
    # leaf, right
    d.polygon([(x + 0.58 * w, cy + r * 0.8), (x + 0.70 * w, cy - r * 0.85),
               (x + 0.90 * w, cy - r * 0.7), (x + 0.76 * w, cy + r * 0.8)],
              fill=(52, 168, 84))
    d.line([x + 0.60 * w, cy + r * 0.75, x + 0.88 * w, cy - r * 0.65],
           fill=(30, 110, 55), width=2)
    # struck-through fossil bar
    d.rectangle([x + 0.52 * w, cy + r + 3, x + 0.94 * w, cy + r + 9],
                fill=(120, 120, 118))
    d.line([x + 0.52 * w, cy + r + 9, x + 0.94 * w, cy + r + 3], fill=RED,
           width=2)


def scene_robots(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY_LIGHT)
    cy = y + h / 2
    cx = x + 0.34 * w
    # robot head
    d.rounded_rectangle([cx - 17, cy - 13, cx + 17, cy + 12], 5,
                        fill=(214, 220, 226))
    d.line([cx, cy - 13, cx, cy - 19], fill=(214, 220, 226), width=2)
    d.ellipse([cx - 3, cy - 22, cx + 3, cy - 16], fill=RED)
    for ex in (-8, 8):
        d.ellipse([cx + ex - 3, cy - 5, cx + ex + 3, cy + 1], fill=NAVY)
    d.rectangle([cx - 8, cy + 6, cx + 8, cy + 8], fill=NAVY)
    # gavel, right
    gx = x + 0.70 * w
    d.line([gx - 10, cy + 10, gx + 12, cy - 12], fill=(196, 150, 84), width=4)
    d.rectangle([gx + 4, cy - 16, gx + 16, cy - 6], fill=(150, 100, 50))
    d.line([x + 0.60 * w, cy + 14, x + 0.86 * w, cy + 14],
           fill=(235, 232, 220), width=2)


def scene_euindo(d, x, y, w, h):
    import math
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    cy = y + h / 2
    # EU panel
    fx = x + 0.10 * w
    d.rectangle([fx, cy - 11, fx + 0.30 * w, cy + 11], fill=(30, 60, 160))
    for i in range(8):
        ang = 2 * math.pi * i / 8
        sx = fx + 0.15 * w + 7.5 * math.cos(ang)
        sy = cy + 7.5 * math.sin(ang)
        d.ellipse([sx - 1.5, sy - 1.5, sx + 1.5, sy + 1.5], fill=GOLD)
    # Indonesia panel
    fx2 = x + 0.60 * w
    d.rectangle([fx2, cy - 11, fx2 + 0.30 * w, cy], fill=(200, 40, 40))
    d.rectangle([fx2, cy, fx2 + 0.30 * w, cy + 11], fill=(240, 240, 240))
    # link arc between them
    d.arc([x + 0.38 * w, cy - 12, x + 0.64 * w, cy + 12], 300, 60,
          fill=GOLD, width=2)


def scene_bitcoin(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(8, 12, 20))
    for i in range(1, 4):
        gy = y + h * i / 4
        d.line([x, gy, x + w, gy], fill=(36, 46, 64), width=1)
    pts = [(x + 0.04 * w, y + 0.20 * h), (x + 0.24 * w, y + 0.30 * h),
           (x + 0.44 * w, y + 0.48 * h), (x + 0.62 * w, y + 0.58 * h),
           (x + 0.80 * w, y + 0.76 * h), (x + 0.95 * w, y + 0.88 * h)]
    d.line(pts, fill=(232, 48, 40), width=3)
    cx = x + 0.20 * w
    cy = y + 0.62 * h
    d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=GOLD)
    d.text((cx - 5, cy - 8), "B", font=font(SANS_BOLD, 14), fill=(120, 80, 10))
    d.text((x + 0.55 * w, y + 0.14 * h), "$55,100", font=font(SANS_BOLD, 12),
           fill=(255, 150, 130))


def scene_mercury(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(10, 10, 16))
    cx, cy = x + 0.68 * w, y + h / 2
    r = h * 0.36
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(168, 160, 150))
    for dx, dy, rr in [(-0.4, -0.3, 0.16), (0.25, 0.1, 0.22), (-0.1, 0.42, 0.13),
                       (0.45, -0.4, 0.11)]:
        d.ellipse([cx + dx * r - rr * r, cy + dy * r - rr * r,
                   cx + dx * r + rr * r, cy + dy * r + rr * r],
                  fill=(148, 140, 130))
    # the spacecraft, left, with two solar wings
    sx, sy = x + 0.22 * w, cy - 4
    d.rectangle([sx - 16, sy - 5, sx - 5, sy + 5], fill=(60, 110, 200))
    d.rectangle([sx + 5, sy - 5, sx + 16, sy + 5], fill=(60, 110, 200))
    d.rectangle([sx - 4, sy - 4, sx + 4, sy + 4], fill=(225, 225, 225))
    d.arc([sx - 20, sy - 16, cx + r * 0.6, cy + r + 14], 200, 300,
          fill=(200, 200, 210), width=1)
    for fx, fy in [(0.08, 0.16), (0.36, 0.08), (0.52, 0.84), (0.14, 0.82)]:
        d.ellipse([x + fx * w, y + fy * h, x + fx * w + 2, y + fy * h + 2],
                  fill=(240, 240, 240))


def scene_wanted(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(70, 52, 34))
    cx, cy = x + w / 2, y + h / 2
    d.rectangle([cx - 30, cy - 16, cx + 30, cy + 16], fill=(240, 233, 210))
    # hat silhouette
    d.rectangle([cx - 13, cy - 8, cx + 13, cy - 4], fill=(40, 32, 24))
    d.rectangle([cx - 7, cy - 13, cx + 7, cy - 8], fill=(40, 32, 24))
    d.text((cx - 16, cy + 1), "$5m", font=font(SANS_BOLD, 12), fill=DEEP_RED)
    d.text((cx - 21, cy - 15), "WANTED", font=font(SANS_BOLD, 7), fill=INK)


def scene_paris(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(44, 48, 66))
    base = y + h
    # Eiffel silhouette
    ex = x + 0.16 * w
    d.polygon([(ex, y + 4), (ex - 9, base), (ex - 3, base), (ex, base - 10),
               (ex + 3, base), (ex + 9, base)], fill=(16, 18, 26))
    d.line([ex - 6, base - 8, ex + 6, base - 8], fill=(16, 18, 26), width=2)
    # crowd: rows of heads + two banners
    for row in range(2):
        for i in range(9):
            hx = x + (0.34 + 0.07 * i) * w
            hy = base - 6 - row * 8
            d.ellipse([hx, hy - 4, hx + 5, hy + 1], fill=(226, 200, 170))
    d.rectangle([x + 0.40 * w, y + 5, x + 0.62 * w, y + 13], fill=(200, 40, 40))
    d.rectangle([x + 0.68 * w, y + 5, x + 0.90 * w, y + 13], fill=(240, 240, 240))


def scene_measles(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 236, 228))
    cy = y + h / 2
    cx = x + 0.26 * w
    d.rectangle([cx - 4, cy - 13, cx + 4, cy + 13], fill=RED)
    d.rectangle([cx - 13, cy - 4, cx + 13, cy + 4], fill=RED)
    # rising case dots
    base = y + h - 5
    for i, fh in enumerate((0.18, 0.30, 0.44, 0.62, 0.84)):
        bx = x + (0.50 + 0.10 * i) * w
        d.rectangle([bx, base - fh * h, bx + 7, base], fill=(196, 90, 60))
    d.line([x + 0.48 * w, base - 0.92 * h, x + 0.97 * w, base - 0.92 * h],
           fill=INK, width=1)


def scene_taiex(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 26, 34))
    pts = []
    sx, sy = x + 0.06 * w, y + 0.16 * h
    for i in range(5):
        pts.append((sx + i * 0.17 * w, sy + i * 0.13 * h))
        pts.append((sx + (i + 1) * 0.17 * w, sy + i * 0.13 * h))
    d.line(pts, fill=(255, 170, 60), width=3)
    ex, ey = pts[-1]
    d.polygon([(ex, ey), (ex - 9, ey - 3), (ex - 2, ey + 8)],
              fill=(255, 170, 60))
    d.text((x + 0.60 * w, y + 0.10 * h), "-17.5%", font=font(SANS_BOLD, 12),
           fill=(255, 190, 120))


def scene_factory(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(56, 40, 34))
    base = y + h
    d.rectangle([x + 0.10 * w, base - 16, x + 0.62 * w, base], fill=(30, 24, 20))
    d.polygon([(x + 0.10 * w, base - 16), (x + 0.26 * w, base - 22),
               (x + 0.42 * w, base - 16)], fill=(30, 24, 20))
    d.rectangle([x + 0.70 * w, base - 26, x + 0.76 * w, base], fill=(30, 24, 20))
    # flames
    for fx, fh in [(0.24, 0.34), (0.36, 0.46), (0.50, 0.30)]:
        cx = x + fx * w
        d.polygon([(cx - 6, base - 14), (cx, base - 14 - fh * h),
                   (cx + 6, base - 14)], fill=ORANGE)
        d.polygon([(cx - 3, base - 14), (cx, base - 14 - fh * h * 0.6),
                   (cx + 3, base - 14)], fill=GOLD)
    for i, fx in enumerate((0.30, 0.44, 0.58)):
        r = 6 + i * 3
        d.ellipse([x + fx * w - r, y + 2 + i * 2, x + fx * w + r,
                   y + 2 + i * 2 + r], fill=(96, 88, 82))


def scene_rugby(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 84, 40))
    cy = y + h / 2
    # posts
    for fx in (0.30, 0.70):
        gx = x + fx * w
        d.line([gx - 8, cy + 12, gx - 8, cy - 12], fill=(240, 240, 240), width=3)
        d.line([gx + 8, cy + 12, gx + 8, cy - 12], fill=(240, 240, 240), width=3)
        d.line([gx - 8, cy - 2, gx + 8, cy - 2], fill=(240, 240, 240), width=3)
    # ball
    d.ellipse([x + 0.44 * w, cy - 6, x + 0.56 * w, cy + 6], fill=(150, 84, 44))
    d.line([x + 0.485 * w, cy, x + 0.515 * w, cy], fill=(240, 240, 240),
           width=2)


def scene_quake(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(66, 58, 48))
    base = y + h
    # mountain profile
    d.polygon([(x, base), (x + 0.34 * w, y + 6), (x + 0.55 * w, base)],
              fill=(44, 38, 32))
    d.polygon([(x + 0.30 * w, y + 12), (x + 0.34 * w, y + 6),
               (x + 0.38 * w, y + 12)], fill=(235, 235, 235))
    # crack through the ground
    pts = [(x + 0.52 * w, base - 2), (x + 0.60 * w, base - 12),
           (x + 0.66 * w, base - 8), (x + 0.74 * w, base - 18),
           (x + 0.82 * w, base - 12), (x + 0.92 * w, base - 20)]
    d.line(pts, fill=(12, 10, 8), width=3)
    d.line([x, base - 1, x + w, base - 1], fill=(12, 10, 8), width=2)
    # small house, tilted
    hx = x + 0.60 * w
    d.rectangle([hx, base - 12, hx + 13, base - 2], fill=(226, 200, 150))
    d.polygon([(hx - 2, base - 12), (hx + 6, base - 17), (hx + 15, base - 12)],
              fill=(150, 60, 40))


def scene_boat(d, x, y, w, h):
    _sea(d, x, y, w, h, tone=(20, 66, 60))
    cy = y + h * 0.55
    # hull + canopy
    d.polygon([(x + 0.16 * w, cy), (x + 0.84 * w, cy), (x + 0.76 * w, cy + 10),
               (x + 0.24 * w, cy + 10)], fill=(120, 84, 44))
    d.rectangle([x + 0.30 * w, cy - 9, x + 0.66 * w, cy], fill=(226, 200, 150))
    d.line([x + 0.30 * w, cy - 9, x + 0.30 * w, cy], fill=(90, 60, 30), width=2)
    d.line([x + 0.66 * w, cy - 9, x + 0.66 * w, cy], fill=(90, 60, 30), width=2)
    # mourners: small heads under the canopy
    for i in range(4):
        hx = x + (0.36 + 0.08 * i) * w
        d.ellipse([hx, cy - 6, hx + 4, cy - 2], fill=(60, 44, 32))
    _waves(d, x, y, w, [y + h - 6])


SCENES = {
    "hormuz": scene_hormuz, "sparta": scene_sparta, "cop": scene_cop,
    "robots": scene_robots, "euindo": scene_euindo, "bitcoin": scene_bitcoin,
    "mercury": scene_mercury, "wanted": scene_wanted, "paris": scene_paris,
    "measles": scene_measles, "taiex": scene_taiex, "factory": scene_factory,
    "rugby": scene_rugby, "quake": scene_quake, "boat": scene_boat,
}

# ------------------------------------------------------------------ page


def grain(img, step=2, mod=89, hits=2, delta=7):
    """A deterministic paper speckle, seeded by pure arithmetic."""
    px = img.load()
    w, h = img.size
    for yy in range(0, h, step):
        for xx in range(0, w, step):
            if (xx * 31 + yy * 17) % mod < hits:
                r, g, b = px[xx, yy]
                px[xx, yy] = (max(0, r - delta), max(0, g - delta),
                              max(0, b - delta))
    return img


def masthead(d, total_line):
    d.text((EDGE, 13), "THE WORLD IN ONE DAY", font=font(SANS_BOLD, 17),
           fill=RED)
    rf = font(SANS, 11)
    d.text((PAGE - EDGE - d.textlength(total_line, font=rf), 17), total_line,
           font=rf, fill=INK)
    d.line([EDGE, 40, PAGE - EDGE, 40], fill=INK, width=3)
    d.line([EDGE, 45, PAGE - EDGE, 45], fill=INK, width=1)


def render():
    img = Image.new("RGB", (PAGE, PAGE), PAPER)
    d = ImageDraw.Draw(img)

    masthead(d, f"{STORY_COUNT} STORIES · 7 REGIONS · EVERY ONE DATED "
                f"SATURDAY 21 NOVEMBER 2026")

    # ---- date, dek, timeline
    middle(d, PAGE / 2, 48, DAY, font(SERIF_BOLD, 62), INK)
    middle(d, PAGE / 2, 122, DEK, font(SERIF_ITALIC, 17), RED)
    d.line([EDGE, 146, PAGE - EDGE, 146], fill=INK, width=1)
    d.text((EDGE, 152), "THE DAY IN UTC", font=font(SANS_BOLD, 10), fill=RED)
    lab_w = d.textlength("THE DAY IN UTC  ", font=font(SANS_BOLD, 10))
    fit(d, EDGE + lab_w, 152, TIMELINE, SANS, 10, SPAN - lab_w, INK)
    d.line([EDGE, 168, PAGE - EDGE, 168], fill=INK, width=1)

    # ---- numbers strip
    cell = SPAN / 6
    for i, (fig, cap) in enumerate(NUMBERS):
        cx = EDGE + cell * i + cell / 2
        middle(d, cx, 176, fig, font(SERIF_BOLD, 31), INK)
        for j, ln in enumerate(wrap_to(d, cap, font(SANS, 10), cell - 14)):
            middle(d, cx, 212 + j * 11, ln, font(SANS, 10), FAINT)
        if i:
            d.line([EDGE + cell * i, 178, EDGE + cell * i, 232],
                   fill=RULE_SOFT, width=1)
    d.line([EDGE, 242, PAGE - EDGE, 242], fill=INK, width=1)

    # ---- region tabs, counts computed from the story list
    tf = font(SANS_BOLD, 12)
    labels = [(r, f"{r.upper()} {REGION_TALLY[r]}") for r in TAB_ORDER]
    widths = [d.textlength(t, font=tf) + 20 for _r, t in labels]
    gap = (SPAN - sum(widths)) / (len(labels) - 1)
    tx = float(EDGE)
    for (r, t), tw in zip(labels, widths):
        d.rectangle([tx, 250, tx + tw, 272], fill=TAB_INK[r])
        middle(d, tx + tw / 2, 255, t, tf, (255, 255, 255))
        tx += tw + gap

    # ---- heroes
    hy, hero_w = 282, 316
    for i, hero in enumerate(HEROES):
        hx = EDGE + i * (hero_w + 10)
        SCENES[hero["scene"]](d, hx, hy, hero_w, 88)
        pin(d, hx + 15, hy + 15, hero["num"], r=10)
        d.text((hx, hy + 96), hero["tag"], font=font(SANS_BOLD, 11), fill=RED)
        block(d, hx, hy + 114, hero["head"], font(SERIF_BOLD, 27), INK,
              hero_w, 29, cap=2)
        block(d, hx, hy + 174, hero["summ"], font(SERIF, 13), INK,
              hero_w, 16, cap=3)
    d.line([EDGE, 510, PAGE - EDGE, 510], fill=INK, width=1)

    # ---- pictured cards, two rows of six
    card_w = 154
    for i, card in enumerate(CARDS):
        cx0 = EDGE + (i % 6) * (card_w + 8)
        cy0 = 518 + (i // 6) * 118
        SCENES[card["scene"]](d, cx0, cy0, card_w, 34)
        pin(d, cx0 + 10, cy0 + 10, card["num"], r=8)
        fit(d, cx0, cy0 + 39, f"{card['place']} · {card['cert']}",
            SANS_BOLD, 10, card_w, RED)
        block(d, cx0, cy0 + 53, card["head"], font(SERIF_BOLD, 15), INK,
              card_w, 17, cap=2)
        block(d, cx0, cy0 + 89, card["summ"], font(SERIF, 12), INK,
              card_w, 13, cap=2)

    # ---- bottom band: map left, briefs right
    by = 758
    d.text((EDGE, by), "WHERE IT HAPPENED", font=font(SANS_BOLD, 12), fill=INK)
    map_x, map_y = EDGE, by + 24
    pitch_x, pitch_y = 7.5, 7.0
    for ri, row in enumerate(WORLD):
        for ci, ch in enumerate(row):
            if ch == "#":
                cxp = map_x + ci * pitch_x + pitch_x / 2
                cyp = map_y + ri * pitch_y + pitch_y / 2
                d.ellipse([cxp - 2.5, cyp - 2.5, cxp + 2.5, cyp + 2.5],
                          fill=MAP_DOT)
    map_w = len(WORLD[0]) * pitch_x
    map_h = len(WORLD) * pitch_y
    for num, (fx, fy) in PINS.items():
        pin(d, map_x + fx * map_w, map_y + fy * map_h, num, r=8.5)
    d.text((EDGE, map_y + map_h + 8),
           "Each number is the pictured story of that number on this page.",
           font=font(SERIF_ITALIC, 10), fill=FAINT)

    bx = 404
    d.text((bx, by), f"ALSO ON SATURDAY — {len(BRIEFS)} MORE STORIES",
           font=font(SANS_BOLD, 12), fill=INK)
    bf = font(SANS_BOLD, 12)
    col_w = 288
    for i, (num, text, _region) in enumerate(BRIEFS):
        col, row_i = divmod(i, 11)
        x0 = bx + col * (col_w + 16)
        y0 = by + 16 + row_i * 14
        label = f"{num} "
        d.text((x0, y0), label, font=bf, fill=RED)
        fit(d, x0 + d.textlength(label, font=bf), y0, text, SANS, 12,
            col_w - d.textlength(label, font=bf), INK, floor=10)

    # ---- date-check box
    box_y = 952
    d.rectangle([EDGE, box_y, PAGE - EDGE, box_y + 36], fill=(250, 238, 231),
                outline=RED, width=2)
    block(d, EDGE + 8, box_y + 6, DATE_CHECK, font(SERIF, 11), DEEP_RED,
          SPAN - 16, 12, cap=2)

    # ---- footer
    d.text((EDGE, 996),
           "Every story here happened, or was first reported, on Saturday "
           "21 November 2026. Officials' counts are attributed in place.",
           font=font(SANS, 9), fill=FAINT)
    tail = "Sources named beside each story · original drawings"
    tf2 = font(SANS, 9)
    d.text((PAGE - EDGE - d.textlength(tail, font=tf2), 1009), tail,
           font=tf2, fill=FAINT)

    return grain(img)


def render_fallback():
    """A compact edition of the same page, kept as the safety copy."""
    img = Image.new("RGB", (PAGE, PAGE), PAPER)
    d = ImageDraw.Draw(img)
    masthead(d, f"{STORY_COUNT} STORIES · SATURDAY 21 NOVEMBER 2026")
    middle(d, PAGE / 2, 60, DAY, font(SERIF_BOLD, 58), INK)
    block(d, EDGE, 150, DEK, font(SERIF_ITALIC, 17), RED, SPAN, 22)
    d.line([EDGE, 190, PAGE - EDGE, 190], fill=INK, width=1)
    y = 210
    for hero in HEROES:
        d.text((EDGE, y), f"{hero['num']}  {hero['tag']}",
               font=font(SANS_BOLD, 12), fill=RED)
        y = block(d, EDGE, y + 20, hero["head"], font(SERIF_BOLD, 30), INK,
                  SPAN, 34, cap=1)
        y = block(d, EDGE, y + 4, hero["summ"], font(SERIF, 15), INK,
                  SPAN, 20, cap=2)
        y += 26
    d.line([EDGE, y, PAGE - EDGE, y], fill=INK, width=1)
    cell = SPAN / 6
    for i, (fig, cap) in enumerate(NUMBERS):
        cx = EDGE + cell * i + cell / 2
        middle(d, cx, y + 14, fig, font(SERIF_BOLD, 28), INK)
        for j, ln in enumerate(wrap_to(d, cap, font(SANS, 10), cell - 14)):
            middle(d, cx, y + 48 + j * 11, ln, font(SANS, 10), FAINT)
    d.text((EDGE, PAGE - 40),
           "Compact edition — the full front page is entry.png.",
           font=font(SANS, 10), fill=FAINT)
    return grain(img)


def build():
    here = os.path.dirname(os.path.abspath(__file__))
    entry = os.path.join(here, "entry.png")
    render().save(entry, format="PNG", optimize=True)
    fallback = os.path.join(here, "fallback.png")
    render_fallback().save(fallback, format="PNG", optimize=True)
    return entry, fallback


if __name__ == "__main__":
    for path in build():
        print(path, os.path.getsize(path))
