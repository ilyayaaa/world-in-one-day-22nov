"""Draw 'The World in One Day: Sunday 22 November 2026' as one PNG.

Everything (scenes, map, type) is drawn in code with Pillow at 2x and
scaled down to 1024 x 1024.  Facts come from wire/RSS items dated
22 November 2026 in at least one time zone; each card names its outlet.

    python3 tools/build.py            -> assets/entry.png
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "entry.png")
S = 2                      # supersampling factor
W = H = 1024

FD = "/usr/share/fonts/truetype/dejavu/"
_fonts = {}


def font(kind, px):
    name = {
        "serif": "DejaVuSerif-Bold.ttf",
        "serifr": "DejaVuSerif.ttf",
        "serifi": "DejaVuSerif-Italic.ttf",
        "sans": "DejaVuSans.ttf",
        "sansb": "DejaVuSans-Bold.ttf",
        "cond": "DejaVuSansCondensed.ttf",
        "condb": "DejaVuSansCondensed-Bold.ttf",
    }[kind]
    key = (name, px)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(FD + name, int(px * S))
    return _fonts[key]


# palette
PAPER = (247, 242, 232)
INK = (22, 26, 40)
NAVY = (24, 36, 66)
RED = (178, 28, 36)
GREY = (96, 96, 100)
RULE = (200, 192, 178)
WHITE = (255, 255, 255)

DATE = "Sunday 22 November 2026"

# ---------------------------------------------------------------- stories
# region, place, tag (red label), figure box, source chip, headline, body,
# outlet, lat, lon, scene
LEADS = [
    dict(region="Europe", place="ANTALYA, TURKEY", topic="CLIMATE",
         tag="COP31: DEAL CLOSE", fig="~200 nations", chip="Summit president",
         head="COP31 climate talks close in on a final deal",
         body="A new package lands after a fight over fossil fuels; delegations "
              "have until 03:00 GMT to object before a final plenary.",
         outlet="Reuters, BBC", lat=36.9, lon=30.7, scene="cop"),
    dict(region="Europe", place="KYIV, UKRAINE", topic="WAR",
         tag="UKRAINE: BARRAGE", fig="400+ drones", chip="Officials' count",
         head="Russia fires 400 drones and 110 missiles",
         body="One of the war's largest overnight attacks; at least seven "
              "people are killed in Kyiv.",
         outlet="Al Jazeera", lat=50.4, lon=30.5, scene="barrage"),
    dict(region="Middle East", place="MANAMA, BAHRAIN", topic="IRAN WAR",
         tag="BAHRAIN: STRUCK", fig="2 bases", chip="Bahrain govt",
         head="Iran strikes US bases in Bahrain",
         body="An industrial site burns, no injuries; tankers are hit in "
              "Hormuz.",
         outlet="Al Jazeera, CNA", lat=26.2, lon=50.6, scene="bahrain"),
]

CARDS = [
    dict(region="Europe", place="GULF OF FINLAND", tag="SHIP ABLAZE",
         chip="Finnish forces", head="Russian cargo ship burns after drone strike",
         body="Finland says Ukraine was likely behind it.",
         outlet="BBC", lat=60.0, lon=26.5, scene="ship"),
    dict(region="Europe", place="KRYVYI RIH", tag="2 DEAD, 60 HURT",
         chip="Officials' count", head="Strike hits Zelensky's home city",
         body="Russian strike on the central Ukrainian city.",
         outlet="Al Jazeera", lat=47.9, lon=33.4, scene="ruin"),
    dict(region="Africa", place="BAYELSA, NIGERIA", tag="24 DEAD",
         chip="Emergency agency", head="Boat carrying mourners capsizes",
         body="Passengers were going to a funeral.",
         outlet="DW, Sky News", lat=4.9, lon=6.3, scene="boat"),
    dict(region="Middle East", place="JERUSALEM", tag="COALITION TALKS",
         chip="Party statement", head="Eisenkot invites Likud to talks",
         body="He seeks the broadest possible government.",
         outlet="Straits Times", lat=31.8, lon=35.2, scene="podium"),
    dict(region="Middle East", place="GAZA", tag="3 KILLED",
         chip="Witnesses", head="Strike hits food aid vehicle",
         body="Three Palestinians die in an air attack.",
         outlet="Al Jazeera, Reuters", lat=31.5, lon=34.45, scene="truck"),
    dict(region="Americas", place="SINALOA, MEXICO", tag="11 DEAD",
         chip="Officials' count", head="'El Chapo Isidro' caught; violence follows",
         body="FBI top-ten fugitive held after a shoot-out.",
         outlet="Sky News, BBC", lat=25.0, lon=-107.5, scene="raid"),
    dict(region="Middle East", place="TEHRAN, IRAN", tag="POWER CUTS",
         chip="Officials", head="Iran to ration electricity",
         body="War damage hits the energy network.",
         outlet="Straits Times", lat=35.7, lon=51.4, scene="power"),
    dict(region="Americas", place="WASHINGTON", tag="SEC PROBE",
         chip="Media report", head="Nvidia faces US accounting probe",
         body="The SEC inquiry is at an early stage.",
         outlet="Straits Times", lat=38.9, lon=-77.0, scene="chip"),
    dict(region="Americas", place="BRASILIA, BRAZIL", tag="BOLSONARO: ICU",
         chip="Hospital", head="Bolsonaro in intensive care",
         body="Ex-president stable, breathing on his own.",
         outlet="Al Jazeera, Reuters", lat=-15.8, lon=-47.9, scene="hospital"),
    dict(region="Asia-Pacific", place="CANBERRA", tag="AUKUS ROW",
         chip="Minister", head="Marles rejects US report on AUKUS subs",
         body="He says the budget office is wrong.",
         outlet="ABC, Reuters", lat=-35.3, lon=149.1, scene="sub"),
]

ALSO = [
    ("Americas", "US", "FBI looks into apparent hack of its crime database", "BBC"),
    ("Americas", "US", "Teen gamer and his mother help FBI rescue a girl", "BBC"),
    ("Americas", "US", "Midterm loss corners Vance as 2028 field widens", "ST"),
    ("Middle East", "Saudi Arabia", "Air defences down a missile", "Investing.com"),
    ("Middle East", "Lebanon", "Aoun demands Israeli withdrawal", "Al Jazeera"),
    ("Middle East", "Iran", "President warns of a 'silent economic war'", "Al Jazeera"),
    ("Middle East", "Hormuz", "Lewis Pugh swims strait as tanker is struck", "BBC"),
    ("Europe", "Moldova", "Reports a Russian airspace breach", "Kyiv Ind."),
    ("Europe", "Belgium", "Air traffic to halt in 23 Nov national strike", "ST"),
    ("Europe", "Germany", "IG Metall widens car and shipyard strikes", "Reuters"),
    ("Europe", "Portugal", "Thousands march in Lisbon on living costs", "Reuters"),
    ("Europe", "Denmark", "Expels Russian attache over rapper plot", "Guardian"),
    ("Asia-Pacific", "Bangladesh", "30 Awami League homes set on fire", "TOI"),
    ("Asia-Pacific", "Australia", "Fred Nile, ex-NSW MP, dies aged 92", "ABC"),
    ("Asia-Pacific", "Australia", "Bystanders pull driver from burning car", "ABC"),
    ("Asia-Pacific", "Melbourne", "70 years since the 1956 Olympics opened", "ABC"),
    ("World", "Trade", "EU and Indonesia sign deal after 10 years", "DW"),
    ("World", "Rugby", "England beat New Zealand 37-12", "Reuters"),
    ("World", "Rugby", "France beat Argentina to reach the final", "Reuters"),
    ("World", "Football", "Arsenal 2-2 Newcastle; Leeds 4-1 at Chelsea", "BBC"),
    ("World", "Tennis", "Zverev v Alcaraz in today's ATP Finals final", "TOI"),
    ("World", "Football", "Liverpool host Manchester United today", "Al Jazeera"),
]

NUMBERS = [
    ("~200", "nations at the COP31 talks"),
    ("03:00", "GMT deadline for objections"),
    ("400+", "drones fired at Ukraine"),
    ("110", "missiles in the same night"),
    ("7+", "people killed in Kyiv"),
    ("2", "US bases targeted in Bahrain"),
]

REGION_ORDER = ["Europe", "Middle East", "Americas", "Asia-Pacific", "Africa", "World"]
REGION_COL = {
    "Europe": (40, 70, 140), "Middle East": (178, 28, 36),
    "Americas": (30, 120, 90), "Asia-Pacific": (200, 120, 20),
    "Africa": (120, 70, 40), "World": (90, 60, 130),
}

# --------------------------------------------------------------- helpers


def z(v):
    return int(round(v * S))


def box(b):
    return [z(b[0]), z(b[1]), z(b[2]), z(b[3])]


def text(d, xy, s, f, fill=INK, anchor="la"):
    d.text((z(xy[0]), z(xy[1])), s, font=f, fill=fill, anchor=anchor)


def tw(s, f):
    return f.getlength(s) / S


def wrap(s, f, width, max_lines):
    words, lines, cur = s.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if tw(t, f) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    lines.append(cur)
    if len(lines) > max_lines:
        raise ValueError("text too long for %d lines: %r" % (max_lines, s))
    return lines


def para(d, x, y, s, f, width, max_lines, lh, fill=INK):
    lines = wrap(s, f, width, max_lines)
    for i, ln in enumerate(lines):
        text(d, (x, y + i * lh), ln, f, fill)
    return y + len(lines) * lh


def grad(img, top, bot):
    w, h = img.size
    d = ImageDraw.Draw(img)
    for yy in range(h):
        t = yy / max(1, h - 1)
        c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        d.line([(0, yy), (w, yy)], fill=c)


def glow(img, cx, cy, r, col):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).ellipse([cx - r, cy - r, cx + r, cy + r], fill=col + (150,))
    lay = lay.filter(ImageFilter.GaussianBlur(r / 2))
    img.alpha_composite(lay)


def flames(d, x, y, w, h, rnd):
    """Row of flame tongues standing on the line y, spread over width w."""
    n = max(3, int(w / (h * 0.45)))
    for i in range(n):
        cx = x + w * (i + 0.5) / n
        hh = h * (0.6 + 0.4 * rnd.random())
        ww = w / n * 0.75
        d.polygon([(cx - ww, y), (cx, y - hh), (cx + ww, y)], fill=(236, 110, 30))
        d.polygon([(cx - ww * 0.5, y), (cx, y - hh * 0.6), (cx + ww * 0.5, y)],
                  fill=(250, 200, 60))


def smoke(d, x, y, h, rnd, col=(70, 70, 78)):
    for i in range(7):
        r = h * (0.12 + 0.05 * i)
        cx = x + i * h * 0.12 + rnd.uniform(-3, 3) * S
        cy = y - i * h * 0.13
        d.ellipse([cx - r, cy - r * 0.8, cx + r, cy + r * 0.8], fill=col)


def person(d, x, y, s, body, head=(214, 170, 130)):
    """Head circle + rounded body, feet at y."""
    d.rounded_rectangle([x - s * 0.45, y - s * 1.4, x + s * 0.45, y], radius=s * 0.3, fill=body)
    d.ellipse([x - s * 0.32, y - s * 2.05, x + s * 0.32, y - s * 1.42], fill=head)


def skyline(d, w, base, rnd, col=(18, 22, 40), lit=(250, 210, 110), hmax=0.55):
    x = 0
    while x < w:
        bw = rnd.randint(int(w * 0.04), int(w * 0.09))
        bh = rnd.randint(int(base * 0.25), int(base * hmax))
        d.rectangle([x, base - bh, x + bw - 2 * S, base], fill=col)
        for wy in range(int(base - bh + 5 * S), int(base - 4 * S), int(6 * S)):
            for wx in range(int(x + 3 * S), int(x + bw - 5 * S), int(6 * S)):
                if rnd.random() < 0.35:
                    d.rectangle([wx, wy, wx + 2 * S, wy + 2 * S], fill=lit)
        x += bw


# ----------------------------------------------------------------- scenes
# Each scene draws on its own RGBA tile of size (w, h) in pixels, so it can
# never spill out of its frame.


def sc_cop(img, rnd):
    w, h = img.size
    grad(img, (120, 196, 200), (214, 236, 226))
    d = ImageDraw.Draw(img)
    # globe
    gx, gy, gr = w * 0.16, h * 0.42, h * 0.28
    glow(img, gx, gy, gr * 1.3, (255, 255, 255))
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(52, 120, 186))
    for (ox, oy, rx, ry) in [(-0.4, -0.3, 0.35, 0.25), (0.25, 0.1, 0.4, 0.3), (-0.2, 0.45, 0.3, 0.18)]:
        d.ellipse([gx + ox * gr - rx * gr, gy + oy * gr - ry * gr,
                   gx + ox * gr + rx * gr, gy + oy * gr + ry * gr], fill=(84, 168, 96))
    # thermometer
    tx = w * 0.34
    d.rounded_rectangle([tx - 5 * S, h * 0.12, tx + 5 * S, h * 0.66], radius=5 * S, fill=WHITE)
    d.rounded_rectangle([tx - 2.5 * S, h * 0.3, tx + 2.5 * S, h * 0.66], radius=2 * S, fill=RED)
    d.ellipse([tx - 9 * S, h * 0.62, tx + 9 * S, h * 0.62 + 18 * S], fill=RED)
    # clock at 3 o'clock
    cx, cy, cr = w * 0.88, h * 0.36, h * 0.2
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=WHITE, outline=INK, width=3 * S)
    for k in range(12):
        a = k / 12 * 2 * math.pi
        d.line([(cx + math.sin(a) * cr * 0.8, cy - math.cos(a) * cr * 0.8),
                (cx + math.sin(a) * cr * 0.92, cy - math.cos(a) * cr * 0.92)], fill=INK, width=S)
    d.line([(cx, cy), (cx, cy - cr * 0.75)], fill=INK, width=2 * S)
    d.line([(cx, cy), (cx + cr * 0.5, cy)], fill=INK, width=3 * S)
    # delegates behind a long table, flags on the table
    ground = h * 0.86
    d.rectangle([0, ground, w, h], fill=(70, 110, 90))
    cols = [(40, 60, 110), (150, 40, 50), (60, 60, 60), (30, 110, 90), (120, 90, 40)]
    for i in range(9):
        person(d, w * (0.42 + i * 0.06), h * 0.74, h * 0.13, cols[i % 5])
    d.rectangle([w * 0.38, h * 0.66, w * 0.96, h * 0.76], fill=(120, 80, 50))
    d.rectangle([w * 0.38, h * 0.76, w * 0.40, ground], fill=(90, 60, 40))
    d.rectangle([w * 0.94, h * 0.76, w * 0.96, ground], fill=(90, 60, 40))
    fcol = [RED, (30, 90, 170), (240, 190, 40), (30, 130, 70), WHITE]
    for i in range(5):
        fx = w * (0.45 + i * 0.1)
        d.line([(fx, h * 0.66), (fx, h * 0.5)], fill=INK, width=S)
        d.rectangle([fx, h * 0.5, fx + 12 * S, h * 0.57], fill=fcol[i])


def sc_barrage(img, rnd):
    w, h = img.size
    grad(img, (10, 14, 40), (60, 40, 70))
    d = ImageDraw.Draw(img)
    for _ in range(60):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h * 0.5)
        d.ellipse([x, y, x + 1.5 * S, y + 1.5 * S], fill=(220, 220, 240))
    glow(img, w * 0.55, h * 0.78, h * 0.35, (255, 120, 40))
    d = ImageDraw.Draw(img)
    # missile trails
    for i in range(9):
        x0 = w * (0.05 + i * 0.11) + rnd.uniform(-10, 10) * S
        x1 = x0 + w * 0.12
        y1 = h * rnd.uniform(0.35, 0.6)
        d.line([(x0, -5), (x1, y1)], fill=(230, 220, 200), width=2 * S)
        d.ellipse([x1 - 4 * S, y1 - 4 * S, x1 + 4 * S, y1 + 4 * S], fill=(255, 150, 40))
    # drones as small deltas
    for _ in range(26):
        x, y = rnd.uniform(0, w), rnd.uniform(h * 0.08, h * 0.45)
        s = 4 * S
        d.polygon([(x - s, y), (x + s, y - s * 0.4), (x + s, y + s * 0.4)], fill=(30, 30, 30))
        d.polygon([(x - s, y), (x + s, y - s * 0.4), (x + s, y + s * 0.4)], outline=(200, 200, 210))
    skyline(d, w, h, rnd)
    flames(d, w * 0.48, h, w * 0.14, h * 0.25, rnd)


def sc_bahrain(img, rnd):
    w, h = img.size
    grad(img, (36, 30, 70), (230, 130, 70))
    d = ImageDraw.Draw(img)
    d.ellipse([w * 0.82, h * 0.1, w * 0.82 + 22 * S, h * 0.1 + 22 * S], fill=(250, 240, 210))
    # missile arcs
    for k in range(3):
        pts = []
        for t in range(41):
            u = t / 40
            pts.append((w * (0.02 + 0.33 * u + k * 0.05), h * (0.5 - 0.42 * math.sin(math.pi * u * 0.9))))
        d.line(pts, fill=(250, 230, 200), width=2 * S)
        ex, ey = pts[-1]
        d.ellipse([ex - 4 * S, ey - 4 * S, ex + 4 * S, ey + 4 * S], fill=(255, 160, 40))
    # sea and tanker on the right
    sea = h * 0.78
    d.rectangle([0, sea, w, h], fill=(30, 50, 80))
    hx = w * 0.6
    d.polygon([(hx, sea - 12 * S), (w * 0.97, sea - 12 * S), (w * 0.94, sea + 6 * S), (hx + 10 * S, sea + 6 * S)],
              fill=(150, 40, 40))
    d.rectangle([w * 0.9, sea - 26 * S, w * 0.95, sea - 12 * S], fill=(230, 230, 230))
    smoke(d, w * 0.7, sea - 22 * S, h * 0.5, rnd)
    flames(d, w * 0.66, sea - 12 * S, w * 0.1, h * 0.2, rnd)
    # plant on land (left)
    d.rectangle([0, sea - 6 * S, w * 0.5, sea + 2 * S], fill=(196, 160, 110))
    for i in range(3):
        cx = w * (0.08 + i * 0.1)
        d.rectangle([cx - 12 * S, sea - 30 * S, cx + 12 * S, sea - 6 * S], fill=(200, 200, 205))
        d.ellipse([cx - 12 * S, sea - 36 * S, cx + 12 * S, sea - 24 * S], fill=(220, 220, 225))
    d.rectangle([w * 0.4, sea - 56 * S, w * 0.43, sea - 6 * S], fill=(120, 120, 130))
    flames(d, w * 0.15, sea - 30 * S, w * 0.16, h * 0.22, rnd)


def sc_ship(img, rnd):
    w, h = img.size
    grad(img, (30, 34, 56), (90, 90, 110))
    d = ImageDraw.Draw(img)
    sea = h * 0.7
    d.rectangle([0, sea, w, h], fill=(26, 52, 84))
    for i in range(6):
        y = sea + 5 * S + i * 4 * S
        d.line([(rnd.uniform(0, w * 0.3), y), (rnd.uniform(w * 0.6, w), y)], fill=(60, 90, 130), width=S)
    smoke(d, w * 0.45, sea - 16 * S, h * 0.9, rnd)
    d.polygon([(w * 0.12, sea - 12 * S), (w * 0.9, sea - 12 * S), (w * 0.84, sea + 6 * S), (w * 0.18, sea + 6 * S)],
              fill=(120, 36, 36))
    d.rectangle([w * 0.72, sea - 28 * S, w * 0.84, sea - 12 * S], fill=(220, 220, 220))
    for i in range(4):
        d.rectangle([w * (0.22 + i * 0.11), sea - 20 * S, w * (0.31 + i * 0.11), sea - 12 * S],
                    fill=[(40, 90, 150), (180, 120, 40), (60, 120, 70), (140, 50, 50)][i])
    flames(d, w * 0.25, sea - 18 * S, w * 0.4, h * 0.35, rnd)


def sc_ruin(img, rnd):
    w, h = img.size
    grad(img, (70, 76, 96), (170, 150, 140))
    d = ImageDraw.Draw(img)
    base = h * 0.92
    skyline(d, w, base, rnd, col=(50, 54, 70), hmax=0.5)
    # broken block in front with a jagged top
    pts = [(w * 0.3, base), (w * 0.3, h * 0.3), (w * 0.38, h * 0.4), (w * 0.45, h * 0.25),
           (w * 0.52, h * 0.45), (w * 0.6, h * 0.35), (w * 0.6, base)]
    d.polygon(pts, fill=(150, 140, 130))
    for wy in range(int(h * 0.5), int(base - 6 * S), int(10 * S)):
        for wx in range(int(w * 0.33), int(w * 0.57), int(10 * S)):
            d.rectangle([wx, wy, wx + 5 * S, wy + 5 * S], fill=(40, 40, 50))
    smoke(d, w * 0.48, h * 0.35, h * 0.6, rnd, col=(90, 90, 96))
    d.rectangle([0, base, w, h], fill=(90, 80, 70))


def sc_boat(img, rnd):
    w, h = img.size
    grad(img, (150, 190, 210), (220, 230, 220))
    d = ImageDraw.Draw(img)
    d.rectangle([0, h * 0.45, w, h], fill=(70, 110, 90))
    d.rectangle([0, h * 0.55, w, h], fill=(60, 110, 140))
    for i in range(5):
        y = h * 0.62 + i * 5 * S
        d.arc([w * 0.1 + i * 6 * S, y, w * 0.9, y + 10 * S], 200, 340, fill=(140, 180, 200), width=S)
    # upturned hull
    d.chord([w * 0.25, h * 0.48, w * 0.7, h * 0.9], 180, 360, fill=(120, 70, 40))
    # life ring
    cx, cy, r = w * 0.82, h * 0.72, 9 * S
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(240, 110, 30))
    d.ellipse([cx - r * 0.5, cy - r * 0.5, cx + r * 0.5, cy + r * 0.5], fill=(60, 110, 140))
    for i in range(6):
        x = w * (0.04 + i * 0.03)
        d.rectangle([x, h * 0.25, x + 4 * S, h * 0.47], fill=(80, 60, 40))
        d.ellipse([x - 8 * S, h * 0.15, x + 12 * S, h * 0.32], fill=(50, 120, 60))


def sc_podium(img, rnd):
    w, h = img.size
    grad(img, (200, 210, 230), (240, 236, 226))
    d = ImageDraw.Draw(img)
    # parliament facade
    d.rectangle([w * 0.05, h * 0.3, w * 0.95, h * 0.85], fill=(225, 210, 180))
    for i in range(10):
        x = w * (0.09 + i * 0.09)
        d.rectangle([x, h * 0.36, x + 6 * S, h * 0.85], fill=(200, 184, 150))
    d.rectangle([0, h * 0.85, w, h], fill=(150, 140, 120))
    # two figures at lecterns, one flag with blue stripes and a white field
    person(d, w * 0.38, h * 0.85, h * 0.25, (30, 40, 70))
    person(d, w * 0.62, h * 0.85, h * 0.25, (60, 60, 70))
    d.rectangle([w * 0.31, h * 0.62, w * 0.45, h * 0.85], fill=(110, 80, 50))
    d.rectangle([w * 0.55, h * 0.62, w * 0.69, h * 0.85], fill=(110, 80, 50))
    d.line([(w * 0.86, h * 0.85), (w * 0.86, h * 0.2)], fill=INK, width=S)
    d.rectangle([w * 0.86, h * 0.2, w * 0.97, h * 0.42], fill=WHITE)
    d.rectangle([w * 0.86, h * 0.23, w * 0.97, h * 0.26], fill=(30, 70, 170))
    d.rectangle([w * 0.86, h * 0.36, w * 0.97, h * 0.39], fill=(30, 70, 170))


def sc_truck(img, rnd):
    w, h = img.size
    grad(img, (200, 180, 150), (236, 220, 190))
    d = ImageDraw.Draw(img)
    d.rectangle([0, h * 0.8, w, h], fill=(170, 140, 100))
    smoke(d, w * 0.25, h * 0.55, h * 0.8, rnd, col=(90, 86, 84))
    d.rectangle([w * 0.18, h * 0.42, w * 0.62, h * 0.8], fill=WHITE)
    d.rectangle([w * 0.62, h * 0.52, w * 0.78, h * 0.8], fill=(230, 230, 230))
    d.rectangle([w * 0.65, h * 0.56, w * 0.75, h * 0.66], fill=(120, 160, 190))
    d.rectangle([w * 0.36, h * 0.5, w * 0.44, h * 0.72], fill=RED)
    d.rectangle([w * 0.3, h * 0.57, w * 0.5, h * 0.65], fill=RED)
    for x in (0.27, 0.68):
        d.ellipse([w * x - 8 * S, h * 0.8 - 8 * S, w * x + 8 * S, h * 0.8 + 8 * S], fill=INK)
    flames(d, w * 0.18, h * 0.42, w * 0.2, h * 0.25, rnd)


def sc_raid(img, rnd):
    w, h = img.size
    grad(img, (40, 50, 40), (150, 150, 110))
    d = ImageDraw.Draw(img)
    d.rectangle([0, h * 0.8, w, h], fill=(110, 90, 60))
    for i in range(4):
        x = w * (0.06 + i * 0.22)
        d.rectangle([x, h * 0.6, x + 4 * S, h * 0.8], fill=(70, 60, 40))
        d.ellipse([x - 12 * S, h * 0.4, x + 16 * S, h * 0.66], fill=(50, 90, 50))
    # helicopter
    cx, cy = w * 0.6, h * 0.3
    d.ellipse([cx - 26 * S, cy - 10 * S, cx + 16 * S, cy + 10 * S], fill=(30, 40, 30))
    d.rectangle([cx + 10 * S, cy - 3 * S, cx + 52 * S, cy + 1 * S], fill=(30, 40, 30))
    d.line([(cx - 44 * S, cy - 14 * S), (cx + 36 * S, cy - 14 * S)], fill=(20, 20, 20), width=2 * S)
    d.ellipse([cx - 22 * S, cy - 7 * S, cx - 10 * S, cy + 3 * S], fill=(150, 190, 210))
    for i in range(5):
        person(d, w * (0.15 + i * 0.16), h * 0.86, h * 0.17, (60, 70, 50), head=(60, 70, 50))


def sc_power(img, rnd):
    w, h = img.size
    grad(img, (16, 18, 34), (50, 46, 70))
    d = ImageDraw.Draw(img)
    skyline(d, w, h, rnd, col=(10, 12, 24), lit=(60, 60, 70), hmax=0.45)
    # pylon
    px = w * 0.3
    d.line([(px - 20 * S, h), (px, h * 0.1), (px + 20 * S, h)], fill=(170, 170, 180), width=2 * S)
    for yy in (0.25, 0.45):
        d.line([(px - 26 * S, h * yy), (px + 26 * S, h * yy)], fill=(170, 170, 180), width=2 * S)
    d.line([(px + 26 * S, h * 0.25), (w, h * 0.35)], fill=(120, 120, 130), width=S)
    # half lit bulb
    bx, by, br = w * 0.7, h * 0.4, h * 0.22
    d.pieslice([bx - br, by - br, bx + br, by + br], 90, 270, fill=(250, 210, 90))
    d.pieslice([bx - br, by - br, bx + br, by + br], 270, 90, fill=(70, 70, 80))
    d.rectangle([bx - br * 0.45, by + br * 0.8, bx + br * 0.45, by + br * 1.25], fill=(160, 160, 170))


def sc_chip(img, rnd):
    w, h = img.size
    grad(img, (230, 236, 222), (210, 220, 205))
    d = ImageDraw.Draw(img)
    cx, cy, s = w * 0.3, h * 0.5, h * 0.32
    d.rectangle([cx - s, cy - s, cx + s, cy + s], fill=(40, 44, 50))
    d.rectangle([cx - s * 0.6, cy - s * 0.6, cx + s * 0.6, cy + s * 0.6], fill=(118, 185, 0))
    for k in range(-3, 4):
        o = k * s * 0.25
        for (a, b) in [((cx + o, cy - s), (cx + o, cy - s - 6 * S)), ((cx + o, cy + s), (cx + o, cy + s + 6 * S)),
                       ((cx - s, cy + o), (cx - s - 6 * S, cy + o)), ((cx + s, cy + o), (cx + s + 6 * S, cy + o))]:
            d.line([a, b], fill=(160, 160, 160), width=S)
    # falling line
    pts = [(w * 0.52, h * 0.25), (w * 0.62, h * 0.35), (w * 0.7, h * 0.3), (w * 0.8, h * 0.6), (w * 0.94, h * 0.8)]
    d.line(pts, fill=RED, width=3 * S)
    d.polygon([(w * 0.94, h * 0.8), (w * 0.9, h * 0.7), (w * 0.97, h * 0.72)], fill=RED)
    # magnifier
    mx, my, mr = w * 0.48, h * 0.45, h * 0.18
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], outline=INK, width=3 * S)
    d.line([(mx + mr * 0.7, my + mr * 0.7), (mx + mr * 1.6, my + mr * 1.6)], fill=INK, width=4 * S)


def sc_hospital(img, rnd):
    w, h = img.size
    grad(img, (220, 232, 238), (240, 244, 246))
    d = ImageDraw.Draw(img)
    d.rectangle([0, h * 0.84, w, h], fill=(180, 196, 204))
    # bed
    d.rectangle([w * 0.2, h * 0.58, w * 0.7, h * 0.68], fill=WHITE, outline=(120, 130, 140), width=S)
    d.rectangle([w * 0.2, h * 0.4, w * 0.23, h * 0.84], fill=(120, 130, 140))
    d.rectangle([w * 0.67, h * 0.5, w * 0.7, h * 0.84], fill=(120, 130, 140))
    d.ellipse([w * 0.25, h * 0.46, w * 0.25 + 14 * S, h * 0.46 + 14 * S], fill=(214, 170, 130))
    d.rounded_rectangle([w * 0.3, h * 0.52, w * 0.66, h * 0.6], radius=4 * S, fill=(120, 170, 200))
    # monitor with pulse
    d.rectangle([w * 0.76, h * 0.2, w * 0.95, h * 0.5], fill=(20, 30, 40))
    pts = [(w * 0.77, h * 0.36), (w * 0.82, h * 0.36), (w * 0.84, h * 0.25), (w * 0.86, h * 0.45),
           (w * 0.88, h * 0.36), (w * 0.94, h * 0.36)]
    d.line(pts, fill=(80, 230, 120), width=S)
    # red cross
    cx, cy = w * 0.1, h * 0.25
    d.rectangle([cx - 4 * S, cy - 11 * S, cx + 4 * S, cy + 11 * S], fill=RED)
    d.rectangle([cx - 11 * S, cy - 4 * S, cx + 11 * S, cy + 4 * S], fill=RED)


def sc_sub(img, rnd):
    w, h = img.size
    grad(img, (150, 190, 220), (210, 226, 236))
    d = ImageDraw.Draw(img)
    sea = h * 0.5
    grad_sea = Image.new("RGBA", (w, int(h - sea)))
    grad(grad_sea, (40, 90, 140), (16, 40, 70))
    img.alpha_composite(grad_sea, (0, int(sea)))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([w * 0.12, sea - 6 * S, w * 0.82, sea + 16 * S], radius=11 * S, fill=(30, 34, 40))
    d.rectangle([w * 0.44, sea - 22 * S, w * 0.54, sea - 2 * S], fill=(30, 34, 40))
    d.line([(w * 0.49, sea - 22 * S), (w * 0.49, sea - 34 * S)], fill=(30, 34, 40), width=2 * S)
    d.polygon([(w * 0.82, sea + 5 * S), (w * 0.9, sea - 6 * S), (w * 0.9, sea + 16 * S)], fill=(30, 34, 40))
    for i in range(8):
        y = sea + 22 * S + i * 3 * S
        d.line([(rnd.uniform(0, w * 0.4), y), (rnd.uniform(w * 0.5, w), y)], fill=(70, 120, 170), width=S)


SCENES = dict(cop=sc_cop, barrage=sc_barrage, bahrain=sc_bahrain, ship=sc_ship, ruin=sc_ruin,
              boat=sc_boat, podium=sc_podium, truck=sc_truck, raid=sc_raid, power=sc_power,
              chip=sc_chip, hospital=sc_hospital, sub=sc_sub)


def scene(canvas, b, name, seed):
    """Render scene `name` inside 1024-space box b, clipped to that box."""
    x0, y0, x1, y1 = box(b)
    tile = Image.new("RGBA", (x1 - x0, y1 - y0), PAPER + (255,))
    SCENES[name](tile, random.Random(seed))
    canvas.alpha_composite(tile, (x0, y0))


def label(d, x, y, s, f, bg, fg=WHITE, pad=4):
    w_ = tw(s, f)
    hh = f.size / S
    d.rectangle(box([x, y, x + w_ + 2 * pad, y + hh + 2 * pad - 1]), fill=bg)
    text(d, (x + pad, y + pad - 1), s, f, fg)
    return x + w_ + 2 * pad


# -------------------------------------------------------------- world map
CONTINENTS = [
    # rough outlines, (lon, lat)
    [(-168, 66), (-140, 70), (-95, 72), (-80, 64), (-60, 58), (-55, 48), (-70, 42), (-80, 30), (-82, 25),
     (-97, 18), (-88, 15), (-80, 8), (-92, 14), (-105, 20), (-117, 32), (-124, 42), (-124, 49), (-135, 58),
     (-152, 58), (-165, 60)],
    [(-78, 9), (-60, 10), (-50, 0), (-35, -6), (-39, -15), (-48, -26), (-58, -36), (-65, -42), (-70, -54),
     (-74, -42), (-71, -20), (-81, -5), (-78, 2)],
    [(-10, 36), (-9, 43), (-2, 44), (-5, 48), (5, 51), (8, 55), (12, 57), (5, 61), (14, 68), (25, 71),
     (40, 68), (60, 70), (80, 73), (110, 76), (140, 72), (170, 68), (178, 64), (160, 60), (142, 52),
     (135, 43), (128, 35), (121, 30), (120, 22), (108, 20), (106, 10), (100, 5), (98, 15), (92, 22),
     (80, 13), (77, 8), (72, 20), (66, 25), (57, 25), (56, 18), (44, 12), (35, 28), (34, 32), (28, 37),
     (24, 38), (20, 40), (16, 38), (12, 44), (6, 43), (0, 39)],
    [(-17, 15), (-16, 22), (-9, 31), (-5, 36), (10, 37), (20, 32), (32, 31), (34, 28), (43, 12), (51, 12),
     (40, -2), (40, -15), (35, -25), (20, -35), (17, -29), (12, -17), (13, -5), (9, 4), (-8, 4), (-15, 10)],
    [(114, -22), (122, -18), (130, -12), (137, -12), (142, -11), (146, -19), (153, -26), (150, -37),
     (141, -38), (131, -31), (115, -34)],
    [(95, 5), (105, -6), (120, -8), (141, -3), (150, -6), (140, -9), (125, -10), (108, -8)],
    [(130, 31), (135, 34), (140, 36), (142, 42), (140, 45), (137, 37)],
    [(-5, 50), (2, 52), (0, 58), (-6, 58)],
]


def draw_map(canvas, b, pins):
    x0, y0, x1, y1 = b
    d = ImageDraw.Draw(canvas)
    d.rectangle(box(b), fill=(232, 238, 240))
    lon0, lon1, lat0, lat1 = -170, 180, 78, -48

    def proj(lon, lat):
        return (x0 + (lon - lon0) / (lon1 - lon0) * (x1 - x0),
                y0 + (lat - lat0) / (lat1 - lat0) * (y1 - y0))

    mask = Image.new("L", canvas.size, 0)
    md = ImageDraw.Draw(mask)
    for poly in CONTINENTS:
        md.polygon([tuple(z(v) for v in proj(*p)) for p in poly], fill=255)
    step = 5
    yy = y0 + 2
    while yy < y1:
        xx = x0 + 2
        while xx < x1:
            if mask.getpixel((z(xx), z(yy))):
                d.ellipse(box([xx - 1.4, yy - 1.4, xx + 1.4, yy + 1.4]), fill=(176, 160, 130))
            xx += step
        yy += step
    f = font("condb", 9)
    placed = []
    for n, lat, lon in pins:
        px, py = proj(lon, lat)
        # nudge pins that would sit on top of each other
        for (qx, qy) in placed:
            if abs(qx - px) < 11 and abs(qy - py) < 11:
                py += 11
        placed.append((px, py))
        r = 6.5
        d.ellipse(box([px - r, py - r, px + r, py + r]), fill=RED, outline=WHITE, width=S)
        text(d, (px, py + 0.5), str(n), f, WHITE, anchor="mm")


# ------------------------------------------------------------------ page


def build():
    img = Image.new("RGBA", (W * S, H * S), PAPER + (255,))
    d = ImageDraw.Draw(img)
    M = 12
    stories = LEADS + CARDS + [dict(region=a[0]) for a in ALSO]
    counts = {r: sum(1 for s in stories if s["region"] == r) for r in REGION_ORDER}
    n_total = len(stories)
    n_regions = sum(1 for r in REGION_ORDER if counts[r])

    # top tag line
    d.rectangle(box([0, 0, W, 20]), fill=NAVY)
    text(d, (M, 4), "THE WORLD IN ONE DAY", font("sansb", 10.5), WHITE)
    tag = "%d STORIES  ·  %d REGIONS  ·  EVERY ONE DATED %s" % (n_total, n_regions, DATE.upper())
    text(d, (W - M, 4), tag, font("sansb", 10.5), WHITE, anchor="ra")

    # title
    text(d, (W / 2, 24), DATE, font("serif", 60), INK, anchor="ma")
    leads_line = "Climate deal in sight at COP31  ·  Russia's 400-drone barrage on Ukraine  ·  Iran hits US bases in Bahrain"
    text(d, (W / 2, 96), leads_line, font("serifi", 14.5), RED, anchor="ma")
    d.line(box([M, 118, W - M, 118]), fill=INK, width=S)

    # numbers strip
    cw = (W - 2 * M) / 6
    for i, (num, lab) in enumerate(NUMBERS):
        x = M + i * cw
        if i:
            d.line(box([x, 124, x, 158]), fill=RULE, width=S)
        text(d, (x + 8, 121), num, font("serif", 24), RED)
        text(d, (x + 8, 150), lab, font("cond", 10), GREY)
    d.line(box([M, 164, W - M, 164]), fill=RULE, width=S)

    # region tabs, width proportional to count
    x = M
    active = [r for r in REGION_ORDER if counts[r]]
    min_w = 70                      # every tab keeps room for its label
    tot = (W - 2 * M) - min_w * len(active)
    for r in active:
        c = counts[r]
        ww = min_w + tot * c / n_total
        d.rectangle(box([x, 168, x + ww - 2, 184]), fill=REGION_COL[r])
        text(d, (x + ww / 2, 176), "%s %d" % (r.upper(), c), font("condb", 10), WHITE, anchor="mm")
        x += ww

    # three lead panels (first is widest)
    widths = [384, 300, 300]
    x = M
    top = 192
    ph = 124
    for i, s in enumerate(LEADS):
        wv = widths[i]
        scene(img, [x, top, x + wv, top + ph], s["scene"], 100 + i)
        d = ImageDraw.Draw(img)
        label(d, x + 6, top + 6, s["tag"], font("condb", 12 if i == 0 else 11), RED)
        if i == 0:
            label(d, x + 6, top + 27, "TOP STORY", font("condb", 9), INK)
        fw = tw(s["fig"], font("serif", 13)) + 10
        d.rectangle(box([x + wv - fw - 6, top + 6, x + wv - 6, top + 26]), fill=WHITE, outline=INK, width=S)
        text(d, (x + wv - 6 - fw / 2, top + 16), s["fig"], font("serif", 13), INK, anchor="mm")
        label(d, x + 6, top + ph - 21, s["chip"], font("cond", 9.5), (20, 22, 30), pad=4)
        y = top + ph + 6
        text(d, (x, y), "%d  %s · %s" % (i + 1, s["place"], s["topic"]), font("condb", 10), RED)
        y += 14
        hf = font("serif", 19 if i == 0 else 17)
        y = para(d, x, y, s["head"], hf, wv, 2, 22 if i == 0 else 20)
        y += 2
        if y + 2 * 13.5 > 410:
            raise ValueError("lead %d text runs into the cards" % (i + 1))
        para(d, x, y, s["body"] + " (" + s["outlet"] + ")", font("sans", 10.5), wv, 2, 13.5, (50, 50, 56))
        x += wv + 8

    # ten mini cards, two rows of five
    cw = (W - 2 * M - 4 * 8) / 5
    for k, s in enumerate(CARDS):
        row, col = divmod(k, 5)
        x = M + col * (cw + 8)
        y = 412 + row * 142
        d = ImageDraw.Draw(img)
        d.rectangle(box([x, y, x + cw, y + 136]), fill=(252, 249, 242), outline=RULE, width=S)
        scene(img, [x + 1, y + 1, x + cw - 1, y + 62], s["scene"], 200 + k)
        d = ImageDraw.Draw(img)
        label(d, x + 5, y + 5, s["tag"], font("condb", 9.5), RED, pad=3)
        label(d, x + 5, y + 44, s["chip"], font("cond", 8.5), (20, 22, 30), pad=3)
        d.ellipse(box([x + cw - 20, y + 4, x + cw - 4, y + 20]), fill=WHITE, outline=INK, width=S)
        text(d, (x + cw - 12, y + 12.5), str(k + 4), font("condb", 9), INK, anchor="mm")
        yy = y + 67
        text(d, (x + 6, yy), s["place"], font("condb", 8.5), RED)
        yy += 12
        yy = para(d, x + 6, yy, s["head"], font("serif", 12.5), cw - 12, 2, 15)
        para(d, x + 6, y + 110, s["body"] + " (" + s["outlet"] + ")", font("cond", 9.5),
             cw - 12, 2, 11.5, (50, 50, 56))

    # map + also list
    top = 702
    d = ImageDraw.Draw(img)
    text(d, (M, top), "WHERE IT HAPPENED", font("sansb", 11), INK)
    text(d, (M + 140, top + 1.5), "pins match story numbers", font("cond", 9), GREY)
    pins = [(i + 1, s["lat"], s["lon"]) for i, s in enumerate(LEADS + CARDS)]
    draw_map(img, [M, top + 16, M + 372, top + 200], pins)

    d = ImageDraw.Draw(img)
    lx = M + 384
    text(d, (lx, top), "ALSO ON SUNDAY 22 NOVEMBER — %d MORE STORIES" % len(ALSO), font("sansb", 11), INK)
    d.line(box([lx, top + 15, W - M, top + 15]), fill=INK, width=S)
    colw = (W - M - lx) / 2
    for i, (reg, where, what, src) in enumerate(ALSO):
        c, r = divmod(i, 11)
        x = lx + c * (colw + 6)
        y = top + 21 + r * 16.4
        n = i + 14
        text(d, (x, y), str(n), font("condb", 10), RED)
        x2 = x + 18
        text(d, (x2, y), where + ":", font("condb", 10), INK)
        x3 = x2 + tw(where + ": ", font("condb", 10))
        line = what + " (" + src + ")"
        f = font("cond", 10)
        if x3 + tw(line, f) > x + colw - 4:
            raise ValueError("also item too long: " + line)
        text(d, (x3, y), line, f, (40, 40, 46))

    # date check box
    top = 908
    d.rectangle(box([M, top, W - M, top + 54]), outline=RED, width=2 * S, fill=(252, 240, 236))
    text(d, (M + 8, top + 6), "DATE CHECK", font("sansb", 10.5), RED)
    dc = ("Wires read up to 00:50 UTC, Sunday 22 November 2026; every story here was reported or still "
          "developing on 22 November in at least one time zone. Left out as other days' news: the Peru "
          "earthquake (20 Nov local), Russian missiles landing in Poland (19 Nov), the Kerch Bridge strikes "
          "(earlier this week) and the Shenzhen summit (19 Nov).")
    para(d, M + 8, top + 20, dc, font("cond", 10), W - 2 * M - 16, 3, 11.5, INK)

    # footer
    foot = ("Sources: Reuters, BBC, Al Jazeera, DW, The Straits Times, Sky News, CNA, ABC Australia, "
            "Times of India, The Guardian, Kyiv Independent. Every story names its outlet. "
            "Pictures and map: original, drawn in code.")
    para(img and ImageDraw.Draw(img), M, 970, foot, font("cond", 9.5), W - 2 * M, 2, 12, GREY)
    d = ImageDraw.Draw(img)
    d.line(box([M, 1004, W - M, 1004]), fill=RULE, width=S)
    text(d, (M, 1008), "THE WORLD IN ONE DAY", font("condb", 9), INK)
    text(d, (W - M, 1008), "SUNDAY 22 NOVEMBER 2026  ·  ONE PAGE", font("condb", 9), INK, anchor="ra")

    out = img.convert("RGB").resize((W, H), Image.LANCZOS)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    out.save(OUT, optimize=True)
    return OUT


if __name__ == "__main__":
    print(build())
