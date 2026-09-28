"""Paper glyphs: one small schematic per paper, in the same visual language as Fig. 1.

  python3 gen_glyphs.py          -> _tools/artwork/out/glyphs/*.svg (standalone previews)
  python3 gen_glyphs.py --site   -> also writes _includes/glyphs/<id>.html
"""
import math, sys, pathlib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "out"
C = dict(ink="#0C1B2E", ink2="#33445A", muted="#5B6A7D", far="#C7D0DB", surface="#FFFFFF",
         surface2="#E9EDF2", line="#B9C3CF", blue="#1A5FD6", wash="#E3EBF8", maize="#FFCB05")


def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def line(a, b, cls="g-rep", w=1.6, dash=None, cap="round"):
    color = {"g-rep": C["blue"], "g-ink": C["ink"], "g-lead": C["ink2"], "g-far": C["far"], "g-maize": C["maize"]}[cls]
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line class="{cls}" x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}" '
            f'stroke="{color}" stroke-width="{w}" stroke-linecap="{cap}"{d}/>')


def poly(pts, cls="g-ink", w=1.8, dash=None):
    color = {"g-rep": C["blue"], "g-ink": C["ink"], "g-lead": C["ink2"], "g-far": C["far"], "g-maize": C["maize"]}[cls]
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{f(x)},{f(y)}" for x, y in pts)
    return (f'<polyline class="{cls}" points="{p}" fill="none" stroke="{color}" stroke-width="{w}" '
            f'stroke-linecap="round" stroke-linejoin="round"{d}/>')


def node(p, r=3.4, kind="node"):
    if kind == "node":
        return f'<circle class="g-node" cx="{f(p[0])}" cy="{f(p[1])}" r="{r}" fill="{C["surface"]}" stroke="{C["blue"]}" stroke-width="1.5"/>'
    if kind == "body":
        return f'<circle class="g-body" cx="{f(p[0])}" cy="{f(p[1])}" r="{r}" fill="{C["surface"]}" stroke="{C["ink"]}" stroke-width="1.5"/>'
    if kind == "rep":
        return f'<circle class="g-repfill" cx="{f(p[0])}" cy="{f(p[1])}" r="{r}" fill="{C["blue"]}"/>'
    if kind == "ink":
        return f'<circle class="g-inkfill" cx="{f(p[0])}" cy="{f(p[1])}" r="{r}" fill="{C["ink"]}"/>'
    if kind == "grasp":
        return f'<circle class="g-maize" cx="{f(p[0])}" cy="{f(p[1])}" r="{r}" fill="none" stroke="{C["maize"]}" stroke-width="2.2"/>'


def sq(p, s=7, kind="node"):
    x, y = p[0] - s / 2, p[1] - s / 2
    if kind == "node":
        return f'<rect class="g-node" x="{f(x)}" y="{f(y)}" width="{s}" height="{s}" fill="{C["surface"]}" stroke="{C["blue"]}" stroke-width="1.5"/>'
    return f'<rect class="g-repfill" x="{f(x)}" y="{f(y)}" width="{s}" height="{s}" fill="{C["blue"]}"/>'


def rect(x, y, w, h, cls="g-body", rx=0, sw=1.5):
    fill = {"g-body": C["surface"], "g-body2": C["surface2"], "g-wash": C["wash"], "g-maizefill": C["maize"],
            "g-repfill": C["blue"], "g-mutedfill": C["line"]}[cls]
    stroke = f' stroke="{C["ink"]}" stroke-width="{sw}"' if cls in ("g-body", "g-body2", "g-maizefill") else ""
    return f'<rect class="{cls}" x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{rx}" fill="{fill}"{stroke}/>'


def text(x, y, s, rep=False, size=7.5, anchor="start"):
    cls = "g-label g-label-rep" if rep else "g-label"
    fill = C["blue"] if rep else C["ink2"]
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return f'<text class="{cls}" x="{f(x)}" y="{f(y)}" fill="{fill}" font-size="{size}"{a}>{s}</text>'


def arrow(a, b, cls="g-lead", w=1.3, head=4.5):
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    l = (b[0] - head * math.cos(ang - 0.5), b[1] - head * math.sin(ang - 0.5))
    r = (b[0] - head * math.cos(ang + 0.5), b[1] - head * math.sin(ang + 0.5))
    return line(a, b, cls, w) + poly([l, b, r], cls, w)


def ground(x0, x1, y):
    out = [line((x0, y), (x1, y), "g-far", 1.2)]
    return "".join(out)


# ---------------------------------------------------------------------------

def body_transformer():
    n = [(30, 14), (30, 34), (12, 47), (48, 47), (30, 58), (20, 84), (40, 84)]
    E = [(0, 1), (1, 2), (1, 3), (1, 4), (4, 5), (4, 6)]
    o = [line(n[a], n[b], "g-rep", 1.8) for a, b in E]
    for i, p in enumerate(n):
        o.append(sq(p, 8, "fill") if i == 1 else node(p, 3.8))
    o.append(arrow((60, 50), (80, 50)))
    k = len(n)
    adj = [[i == j for j in range(k)] for i in range(k)]
    for a, b in E:
        adj[a][b] = adj[b][a] = True
    x0, y0, c, g = 88, 18, 8.2, 1.0
    for i in range(k):
        for j in range(k):
            o.append(rect(x0 + j * (c + g), y0 + i * (c + g), c, c, "g-repfill" if adj[i][j] else "g-mutedfill", rx=1))
    o.append(text(4, 97, "body graph"))
    o.append(text(88, 97, "attention mask", rep=True))
    return o


def hand(cx, y0, fingers, show_palm=True):
    o = []
    palm = (cx, y0 + 25)
    bases = [-10, -3.5, 3.5, 10]
    for fx, count in zip(bases, fingers):
        if count == 0:
            continue
        pts = [palm] + [(cx + fx * (1 + 0.08 * i), y0 + 19 - 6 * i) for i in range(count)]
        o.append(poly(pts, "g-rep", 1.3))
        for p in pts[1:]:
            o.append(node(p, 2.0))
    o.append(sq(palm, 6, "fill"))
    return o


def get_zero():
    o = []
    rows = [(4, [3, 3, 3, 3]), (36, [3, 0, 3, 3]), (68, [3, 3, 4, 3])]
    for y0, fing in rows:
        o += hand(24, y0, fing)
        o.append(line((40, y0 + 16), (70, 50), "g-lead", 1.1))
    o.append(rect(72, 36, 38, 28, "g-body", rx=4, sw=1.6))
    o.append(text(91, 53.5, "GET", size=9, anchor="middle"))
    o.append(arrow((111, 50), (126, 50)))
    o.append(rect(131, 42, 16, 16, "g-body2", rx=2, sw=1.5))
    o.append(f'<path class="g-maize" d="M130 36 A15 15 0 0 1 150 38" fill="none" stroke="{C["maize"]}" stroke-width="2.2" stroke-linecap="round"/>')
    o.append(poly([(146, 34), (150, 38), (145, 40)], "g-maize", 2.0))
    o.append(text(91, 76, "one policy", anchor="middle"))
    o.append(text(91, 86, "unseen hands", rep=True, anchor="middle"))
    return o


def relic():
    o = [ground(6, 154, 92)]
    # far legs (faint): rear and front on the ground
    o.append(poly([(56, 50), (50, 70), (56, 90)], "g-far", 5))
    o.append(poly([(94, 50), (88, 70), (94, 90)], "g-far", 5))
    # body
    o.append(f'<path class="g-body" d="M42 40 H92 L99 45 L96 51 H40 L36 45.5 Z" fill="{C["surface"]}" stroke="{C["ink"]}" stroke-width="1.6" stroke-linejoin="round"/>')
    # rear near leg: locomotion
    o.append(poly([(48, 49), (42, 69), (48, 89)], "g-ink", 3.2))
    o.append(node((42, 69), 2.6, "body"))
    o.append(node((48, 89), 2.6, "ink"))
    # front near leg raised: manipulation
    o.append(poly([(90, 49), (104, 62), (116, 72)], "g-rep", 3.2))
    o.append(node((104, 62), 2.6))
    # arm: manipulation
    o.append(poly([(84, 40), (96, 20), (114, 30)], "g-rep", 3.0))
    o.append(node((96, 20), 2.6))
    # object held by gripper and foot
    o.append(rect(118, 26, 28, 52, "g-body2", rx=2, sw=1.5))
    o.append(node((117, 31), 4.6, "grasp"))
    o.append(node((117, 72), 4.6, "grasp"))
    o.append(line((8, 10), (18, 10), "g-rep", 3))
    o.append(text(22, 12.5, "manipulation", rep=True))
    o.append(line((8, 21), (18, 21), "g-ink", 3))
    o.append(text(22, 23.5, "locomotion"))
    return o


def tool(ax, ay):
    o = [rect(ax - 7, ay - 7, 8, 14, "g-maizefill", rx=1.5, sw=1.3)]
    o.append(poly([(ax + 1, ay - 5), (ax + 11, ay - 3.5)], "g-ink", 2))
    o.append(poly([(ax + 1, ay + 5), (ax + 11, ay + 3.5)], "g-ink", 2))
    o.append(node((ax - 3, ay), 1.6, "rep"))
    return o


def legato():
    o = []
    ay = 46
    for i, px in enumerate((0, 54, 108)):
        ax = px + 34
        if i == 0:   # human arm holding the tool by its handle
            o.append(poly([(px + 6, 18), (px + 14, 44), (ax - 6, ay + 12)], "g-ink", 3.2))
            o.append(f'<circle class="g-body" cx="{f(ax - 4)}" cy="{f(ay + 12)}" r="4" fill="{C["surface"]}" stroke="{C["ink"]}" stroke-width="1.5"/>')
            o.append(rect(ax - 5, ay + 6, 3, 9, "g-maizefill", rx=1, sw=1.1))
            o.append(text(px + 4, 96, "human"))
        elif i == 1:  # fixed-base arm
            o.append(rect(px + 4, 80, 16, 8, "g-body", rx=1.5))
            o.append(poly([(px + 12, 80), (px + 12, 62), (px + 22, 40), (ax - 7, ay)], "g-ink", 2.6))
            for p in ((px + 12, 62), (px + 22, 40)):
                o.append(node(p, 2.6, "body"))
            o.append(text(px + 4, 96, "arm"))
        else:         # legged manipulator
            o.append(f'<path class="g-body" d="M{px + 4} 62 H{px + 26} L{px + 29} 65 L{px + 27} 68 H{px + 3} L{px + 1} 65 Z" fill="{C["surface"]}" stroke="{C["ink"]}" stroke-width="1.4" stroke-linejoin="round"/>')
            o.append(poly([(px + 7, 67), (px + 5, 76), (px + 8, 86)], "g-ink", 2.2))
            o.append(poly([(px + 23, 67), (px + 21, 76), (px + 24, 86)], "g-ink", 2.2))
            o.append(poly([(px + 22, 62), (px + 26, 46), (ax - 7, ay)], "g-ink", 2.4))
            o.append(node((px + 26, 46), 2.4, "body"))
            o.append(text(px + 4, 96, "legged"))
        o += tool(ax, ay)
    o.append(line((50, 30), (158, 30), "g-rep", 1.1, dash="3 3"))
    o.append(line((52, 8), (52, 90), "g-far", 1, dash="2 3"))
    o.append(line((106, 8), (106, 90), "g-far", 1, dash="2 3"))
    o.append(text(58, 24, "same tool frame", rep=True))
    return o


def vkc():
    y = 44
    o = []
    # world ground at both ends
    for x in (8, 152):
        o.append(line((x, y - 9), (x, y + 9), "g-ink", 1.6))
        for k in range(4):
            dx = -1 if x < 80 else 1
            o.append(line((x, y - 7 + k * 5), (x + dx * 4, y - 4 + k * 5), "g-ink", 1))
    o.append(line((8, y), (60, y), "g-rep", 1.5, dash="4 3"))
    for p, kind in (((20, y), "p"), ((33, y), "p"), ((46, y), "r")):
        o.append(sq(p, 7) if kind == "p" else node(p, 3.6))
    o.append(rect(58, y - 8, 18, 14, "g-body", rx=2))
    o.append(node((62, y + 8), 2.4, "ink"))
    o.append(node((72, y + 8), 2.4, "ink"))
    o.append(poly([(76, y), (88, y), (100, y), (112, y)], "g-ink", 2.2))
    for x in (88, 100):
        o.append(node((x, y), 3.3, "body"))
    o.append(poly([(111, y - 4), (118, y - 3)], "g-ink", 1.8))
    o.append(poly([(111, y + 4), (118, y + 3)], "g-ink", 1.8))
    o.append(node((121, y), 4.2, "grasp"))
    o.append(line((125, y), (152, y), "g-rep", 1.5, dash="4 3"))
    o.append(node((138, y), 3.6))
    o.append(f'<path class="g-rep" d="M131 36 A9 9 0 0 1 145 36" fill="none" stroke="{C["blue"]}" stroke-width="1.2"/>')
    # brackets + labels
    for x0, x1, s, rep in ((14, 50, "virtual base", True), (58, 118, "robot", False), (124, 148, "object", True)):
        o.append(poly([(x0, 62), (x0, 66), (x1, 66), (x1, 62)], "g-lead", 1))
        o.append(text((x0 + x1) / 2, 78, s, rep=rep, anchor="middle"))
    o.append(text(80, 18, "one chain: world → base → arm → object", anchor="middle", size=7))
    return o


def smmp():
    o = []
    rows = [(12, "drawer"), (44, "door"), (76, "cup")]
    for i, (y, obj) in enumerate(rows):
        o.append(f'<circle class="g-node" cx="9" cy="{y}" r="6" fill="{C["surface"]}" stroke="{C["blue"]}" stroke-width="1.3"/>')
        o.append(text(9, y + 2.6, str(i + 1), rep=True, size=7.5, anchor="middle"))
        o.append(rect(22, y - 5, 10, 10, "g-body", rx=1.5, sw=1.3))
        o.append(poly([(32, y), (44, y), (56, y)], "g-ink", 2))
        o.append(node((44, y), 2.8, "body"))
        o.append(poly([(55, y - 3.5), (61, y - 2.5)], "g-ink", 1.6))
        o.append(poly([(55, y + 3.5), (61, y + 2.5)], "g-ink", 1.6))
        o.append(node((64, y), 3.8, "grasp"))
        o.append(line((68, y), (98, y), "g-rep", 1.4, dash="3 3"))
        if obj == "drawer":
            o.append(rect(100, y - 7, 26, 14, "g-body2", rx=1, sw=1.3))
            o.append(sq((136, y), 7))
            o.append(line((128, y), (144, y), "g-rep", 1.1))
            o.append(text(98, y + 15, "prismatic joint", rep=True, size=6.5))
        elif obj == "door":
            o.append(rect(100, y - 9, 6, 18, "g-body2", rx=1, sw=1.3))
            o.append(line((106, y), (130, y), "g-rep", 1.4, dash="3 3"))
            o.append(node((136, y), 3.6))
            o.append(f'<path class="g-rep" d="M130 {y - 6} A8 8 0 0 1 142 {y - 6}" fill="none" stroke="{C["blue"]}" stroke-width="1.1"/>')
            o.append(text(98, y + 15, "revolute joint", rep=True, size=6.5))
        else:
            o.append(f'<path class="g-body2" d="M104 {y - 7} H116 L114 {y + 7} H106 Z" fill="{C["surface2"]}" stroke="{C["ink"]}" stroke-width="1.3" stroke-linejoin="round"/>')
            o.append(line((116, y), (132, y), "g-rep", 1.4, dash="3 3"))
            o.append(sq((136, y), 7, "fill"))
            o.append(text(98, y + 15, "free object", rep=True, size=6.5))
    return o


def skeleton(ox, nodes=False, cls="g-ink"):
    head, neck, pel = (ox + 14, 12), (ox + 14, 18), (ox + 14, 40)
    lh, rh = (ox + 4, 8), (ox + 24, 8)
    lk, rk, lf, rf = (ox + 8, 52), (ox + 20, 52), (ox + 12, 63), (ox + 24, 61)
    sh = (ox + 14, 23)
    o = []
    w = 2.6
    o.append(poly([neck, pel], cls, w))
    o.append(poly([lh, sh, rh], cls, w))
    o.append(poly([lf, lk, pel, rk, rf], cls, w))
    if nodes:
        o.append(rect(ox + 9, 5, 10, 9, "g-body", rx=2, sw=1.4))
        for p in (sh, pel, lk, rk, lh, rh):
            o.append(node(p, 2.5))
    else:
        o.append(f'<circle class="g-body" cx="{f(head[0])}" cy="{f(head[1])}" r="4.5" fill="{C["surface"]}" stroke="{C["ink"]}" stroke-width="1.6"/>')
    return o


def zest():
    o = [ground(4, 156, 86)]
    for ox in (6, 60):
        o.append(f'<path class="g-rep" d="M{ox - 2} 84 Q {ox + 14} {-24} {ox + 30} 84" fill="none" stroke="{C["blue"]}" stroke-width="1" stroke-dasharray="2 3" opacity="0.8"/>')
    o += skeleton(6)
    o += skeleton(60, nodes=True, cls="g-ink")
    o.append(arrow((40, 40), (56, 40), "g-rep", 1.5))
    # quadruped mid-jump
    o.append(f'<path class="g-rep" d="M104 84 Q 128 {-6} 154 84" fill="none" stroke="{C["blue"]}" stroke-width="1" stroke-dasharray="2 3" opacity="0.8"/>')
    o.append(f'<path class="g-body" d="M114 36 H138 L141 39 L139 42 H113 L111 39 Z" fill="{C["surface"]}" stroke="{C["ink"]}" stroke-width="1.4" stroke-linejoin="round"/>')
    o.append(poly([(117, 41), (111, 48), (118, 54)], "g-ink", 2.2))
    o.append(poly([(135, 41), (129, 48), (136, 54)], "g-ink", 2.2))
    o.append(node((111, 48), 2.3))
    o.append(node((129, 48), 2.3))
    o.append(text(4, 97, "human"))
    o.append(text(60, 97, "humanoid", rep=True))
    o.append(text(112, 97, "quadruped", rep=True))
    return o


def uniskill():
    o = []
    for y0 in (8, 50):
        o.append(rect(6, y0, 44, 36, "g-body", rx=2, sw=1.3))
        for k in range(4):
            o.append(rect(8, y0 + 3 + k * 8, 3, 4, "g-mutedfill", rx=0.5))
    # human arm reaching a cup: frame t and t+k
    o.append(poly([(16, 40), (26, 30), (34, 30)], "g-ink", 2.6))
    o.append(node((35, 30), 2.6, "body"))
    o.append(f'<path class="g-body2" d="M38 34 H46 L45 42 H39 Z" fill="{C["surface2"]}" stroke="{C["ink"]}" stroke-width="1.2" stroke-linejoin="round"/>')
    o.append(poly([(16, 82), (28, 74), (38, 70)], "g-ink", 2.6))
    o.append(node((39, 69), 2.6, "body"))
    o.append(f'<path class="g-body2" d="M38 66 H46 L45 74 H39 Z" fill="{C["surface2"]}" stroke="{C["ink"]}" stroke-width="1.2" stroke-linejoin="round"/>')
    o.append(arrow((54, 48), (66, 48)))
    for k in range(6):
        cls = "g-maizefill" if k == 2 else "g-repfill"
        o.append(rect(70, 26 + k * 8, 10, 7, cls, rx=1, sw=1))
    o.append(text(75, 20, "z", rep=True, size=9, anchor="middle"))
    o.append(arrow((84, 48), (96, 48)))
    o.append(rect(100, 16, 54, 64, "g-body", rx=2, sw=1.3))
    o.append(rect(106, 68, 12, 8, "g-body2", rx=1, sw=1.2))
    o.append(poly([(112, 68), (114, 48), (130, 38), (138, 46)], "g-ink", 2.4))
    for p in ((114, 48), (130, 38)):
        o.append(node(p, 2.6))
    o.append(poly([(137, 49), (141, 53)], "g-ink", 1.6))
    o.append(poly([(140, 45), (144, 49)], "g-ink", 1.6))
    o.append(f'<path class="g-body2" d="M140 56 H148 L147 64 H141 Z" fill="{C["surface2"]}" stroke="{C["ink"]}" stroke-width="1.2" stroke-linejoin="round"/>')
    o.append(text(6, 97, "human"))
    o.append(text(75, 97, "skill", rep=True, anchor="middle"))
    o.append(text(154, 97, "robot", anchor="end"))
    return o


def westworld():
    o = []
    # three morphologies, each reduced to a structure graph
    o.append(poly([(8, 12), (34, 12)], "g-ink", 2.4))
    for x in (10, 32):
        o.append(poly([(x, 12), (x - 3, 19), (x, 26)], "g-rep", 1.4))
        o.append(node((x - 3, 19), 2.0))
    o.append(rect(8, 56, 8, 5, "g-body", rx=1, sw=1.2))
    o.append(poly([(12, 56), (14, 46), (26, 40), (36, 46)], "g-rep", 1.4))
    for q in ((14, 46), (26, 40)):
        o.append(node(q, 2.0))
    o.append(node((36, 46), 2.2, "rep"))
    o.append(poly([(20, 70), (20, 82)], "g-ink", 2.4))
    o.append(poly([(20, 82), (14, 90), (12, 97)], "g-rep", 1.4))
    o.append(poly([(20, 82), (26, 90), (28, 97)], "g-rep", 1.4))
    o.append(node((14, 90), 2.0)); o.append(node((26, 90), 2.0))
    for y in (19, 50, 84):
        o.append(line((42, y), (70, 50), "g-lead", 1.0))
    # system-aware mixture of experts
    o.append(f'<path class="g-body" d="M76 42 L84 50 L76 58 L68 50 Z" fill="{C["surface"]}" stroke="{C["ink"]}" stroke-width="1.4" stroke-linejoin="round"/>')
    for i, y in enumerate((20, 42, 64)):
        o.append(line((84, 50), (94, y + 8), "g-lead", 1.0))
        o.append(rect(94, y, 22, 16, "g-repfill" if i == 1 else "g-body", rx=2, sw=1.3))
    o.append(text(105, 13, "experts", rep=True, anchor="middle"))
    # trajectory: history solid, prediction dashed
    o.append(poly([(124, 76), (130, 64), (138, 57)], "g-ink", 2))
    o.append(poly([(138, 57), (146, 46), (154, 30)], "g-rep", 2, dash="3 3"))
    for q in ((124, 76), (130, 64), (138, 57)):
        o.append(node(q, 1.8, "ink"))
    o.append(node((154, 30), 2.4, "rep"))
    o.append(text(139, 94, "rollout", anchor="middle"))
    return o


def articubot():
    o = []
    # cabinet and an opened door as a point cloud
    pts = []
    for x in range(10, 51, 5):
        pts += [(x, 20), (x, 84)]
    for y in range(25, 81, 5):
        pts += [(10, y), (50, y)]
    for i in range(0, 5):
        t = i / 4
        pts += [(50 + 18 * t, 20 + 8 * t), (50 + 18 * t, 84 - 8 * t)]
    for y in range(32, 73, 5):
        pts.append((68, y))
    for q in pts:
        o.append(f'<circle class="g-mutedfill" cx="{f(q[0])}" cy="{f(q[1])}" r="1.3" fill="{C["line"]}"/>')
    o.append(node((66, 52), 2.2, "ink"))
    # weighted displacements toward the goal gripper
    for q in ((58, 34), (60, 70), (46, 50), (68, 40)):
        o.append(line(q, (76, 52), "g-rep", 0.9, dash="2 2"))
    o.append(poly([(80, 46), (74, 46), (74, 58), (80, 58)], "g-rep", 2))
    o.append(node((74, 52), 2.2, "rep"))
    o.append(text(42, 96, "point cloud", anchor="middle"))
    o.append(text(78, 40, "goal", rep=True, anchor="middle"))
    o.append(arrow((88, 52), (100, 52)))
    # two real setups: tabletop arm and arm on a mobile base
    o.append(rect(104, 70, 22, 4, "g-body2", rx=1, sw=1.2))
    o.append(poly([(110, 70), (110, 58), (118, 46), (124, 52)], "g-ink", 2.2))
    o.append(node((110, 58), 2.0, "body")); o.append(node((118, 46), 2.0, "body"))
    o.append(rect(132, 62, 22, 10, "g-body", rx=2, sw=1.3))
    o.append(node((137, 74), 2.2, "ink")); o.append(node((149, 74), 2.2, "ink"))
    o.append(poly([(146, 62), (146, 48), (138, 38), (132, 42)], "g-ink", 2.2))
    o.append(node((146, 48), 2.0, "body")); o.append(node((138, 38), 2.0, "body"))
    o.append(text(129, 94, "zero-shot", rep=True, anchor="middle"))
    return o


GLYPHS = {
    "body-transformer": (body_transformer, "Body graph turned into a transformer attention mask"),
    "get-zero": (get_zero, "Three hand graphs with different fingers feeding one policy that rotates an object"),
    "relic": (relic, "A legged robot using its arm and one front leg to manipulate while three legs walk"),
    "legato": (legato, "The same handheld gripper held by a human, a robot arm and a legged robot"),
    "vkc": (vkc, "A single kinematic chain from world through virtual base joints, robot arm and object joint"),
    "smmp": (smmp, "A sequence of robot-object chains: drawer, door and cup"),
    "zest": (zest, "A human jump retargeted to a humanoid and a quadruped"),
    "uniskill": (uniskill, "Human video frames encoded as a skill vector that conditions a robot arm"),
    "westworld": (westworld, "Different robot structures routed through a mixture of experts to predict trajectories"),
    "articubot": (articubot, "A point cloud of an opened cabinet with a predicted goal gripper, transferred to two robots"),
}


def svg(gid, standalone=False):
    fn, _ = GLYPHS[gid]
    body = "\n  ".join(fn())
    if standalone:
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 100" width="480" height="300" font-family="DejaVu Sans Mono">'
                f'<rect width="160" height="100" fill="#FFFFFF"/>\n  {body}\n</svg>')
    return f'<svg class="glyph" viewBox="0 0 160 100" aria-hidden="true" focusable="false">\n  {body}\n</svg>\n'


if __name__ == "__main__":
    out = OUT / "glyphs"
    out.mkdir(parents=True, exist_ok=True)
    for gid in GLYPHS:
        (out / f"{gid}.svg").write_text(svg(gid, True))
        if "--site" in sys.argv:
            (ROOT / "_includes" / "glyphs" / f"{gid}.html").write_text(svg(gid))
    print("ok", len(GLYPHS))
