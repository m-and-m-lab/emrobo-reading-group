"""Generate Fig. 1 (the body inspector) with consistent kinematics.

  python3 gen_hero.py          -> _tools/artwork/out/hero.svg (standalone preview)
  python3 gen_hero.py --site   -> also writes _includes/figure-body.html

Every drawn element carries a role class (f-*) that main.css re-colors from
theme tokens; presentation attributes hold the light palette as a fallback.
The JS in assets/js/site.js re-poses the arm with the same IK as pose().
"""
import math, sys, pathlib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "out"

C = dict(wash="#E3EBF8", wash2="#C6D6F1", ink="#0C1B2E", ink2="#33445A", muted="#5B6A7D",
         far="#C7D0DB", surface="#FFFFFF", surface2="#E9EDF2", line="#B9C3CF",
         blue="#1A5FD6", maize="#FFCB05")

GROUND = 392
S = (284.0, 186.0)          # shoulder
L1 = L2 = 100.0
FRONT_CLOSED = 512.0        # drawer front x when closed
Q0 = 30.0                   # drawer opening in the static pose
B = (196.0, 218.0)          # floating base (root node)
H1, K1, F1 = (142, 236), (114, 314), (146, 384)
H2, K2, F2 = (306, 236), (278, 314), (310, 384)
COM = (250.0, 209.0)
CAM = (341.0, 214.0)
P = (584.0, 199.0)          # drawer prismatic joint
WORLD = (58.0, GROUND)


def pose(q):
    fx = FRONT_CLOSED - q
    W = (fx - 46.0, 206.0)
    T = (W[0] + 27.0, W[1])
    dx, dy = W[0] - S[0], W[1] - S[1]
    d = math.hypot(dx, dy)
    a = math.acos(min(1.0, d / (L1 + L2)))
    th = math.atan2(dy, dx) - a            # elbow up
    E = (S[0] + L1 * math.cos(th), S[1] + L1 * math.sin(th))
    return dict(fx=fx, W=W, T=T, E=E, bar=fx - 12.0)


def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def pt(p):
    return f"{f(p[0])} {f(p[1])}"


def ellipse_d(c, rx, ry, rot_deg):
    t = math.radians(rot_deg)
    ax, ay = rx * math.cos(t), rx * math.sin(t)
    p1, p2 = (c[0] + ax, c[1] + ay), (c[0] - ax, c[1] - ay)
    return (f"M{pt(p1)} A{f(rx)} {f(ry)} {f(rot_deg)} 1 1 {pt(p2)} "
            f"A{f(rx)} {f(ry)} {f(rot_deg)} 1 1 {pt(p1)} Z")


def occlusion(W):
    top, bot = (W[0] - 2, 197.0), (W[0] - 2, 215.0)
    def ext(p):
        t = (520.0 - CAM[0]) / (p[0] - CAM[0])
        return (520.0, CAM[1] + (p[1] - CAM[1]) * t)
    return f"M{pt(top)} L{pt(ext(top))} L{pt(ext(bot))} L{pt(bot)} Z"


def arrowhead(tip, ang_deg, size=6):
    a = math.radians(ang_deg)
    l = (tip[0] - size * math.cos(a - 0.45), tip[1] - size * math.sin(a - 0.45))
    r = (tip[0] - size * math.cos(a + 0.45), tip[1] - size * math.sin(a + 0.45))
    return f"M{pt(l)} L{pt(tip)} L{pt(r)}"


def label(x, y, text, rep=False, dim=False):
    cls = "f-label f-label-rep" if rep else "f-label"
    fill = C["blue"] if rep else C["ink2"]
    op = ' opacity="0.8"' if dim else ""
    return f'<text class="{cls}" x="{f(x)}" y="{f(y)}" fill="{fill}" font-size="11"{op}>{text}</text>'


def leader(d):
    return f'<path class="f-lead f-leader" d="{d}" fill="none" stroke="{C["ink2"]}" stroke-width="1"/>'


def build(standalone):
    p = pose(Q0)
    W, T, E, fx, bar = p["W"], p["T"], p["E"], p["fx"], p["bar"]
    o = []
    A = o.append
    if standalone:
        A('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 440" width="1440" height="880" font-family="DejaVu Sans Mono">')
        A('<rect width="720" height="440" fill="#F2F4F7"/>')
    else:
        A(f'<svg class="fig1" viewBox="0 0 720 440" role="img" aria-labelledby="fig1-title fig1-desc" data-q0="{f(Q0)}">')
        A('<title id="fig1-title">A legged mobile manipulator opening a drawer, annotated with what a model could know about its body</title>')
        A('<desc id="fig1-desc">Overlays show the kinematic graph, mass and actuation limits, foot contacts and the support polygon, the camera field of view and what the gripper occludes, the arm\'s reach and manipulability, and a virtual kinematic chain that joins the world, the base, the arm and the drawer joint.</desc>')

    A(f'<line class="f-ground" x1="20" y1="{GROUND}" x2="700" y2="{GROUND}" stroke="{C["line"]}" stroke-width="1.5"/>')

    # ---- sensing: FOV and occlusion (drawn first, behind the robot) ----------
    up = CAM[1] - math.tan(math.radians(20)) * (520 - CAM[0])
    dn = CAM[1] + math.tan(math.radians(30)) * (520 - CAM[0])
    A('<g class="layer" data-layer="sensing">')
    A(f'<path class="f-wash" d="M{pt(CAM)} L520 {f(up)} L520 {f(dn)} Z" fill="{C["wash"]}"/>')
    A(f'<path class="f-rep" d="M520 {f(up)} L{pt(CAM)} L520 {f(dn)}" fill="none" stroke="{C["blue"]}" stroke-width="1.2" stroke-dasharray="4 4"/>')
    A(f'<path id="fig-occ" class="f-wash2" d="{occlusion(W)}" fill="{C["wash2"]}"/>')
    A(label(398, 318, "camera FOV", rep=True))
    A(label(398, 331, "+ occlusion", rep=True, dim=True))
    A('</g>')

    # ---- reach: workspace limit and manipulability ---------------------------
    R = L1 + L2
    a0, a1 = math.radians(-62), math.radians(34)
    r0 = (S[0] + R * math.cos(a0), S[1] + R * math.sin(a0))
    r1 = (S[0] + R * math.cos(a1), S[1] + R * math.sin(a1))
    rad = math.degrees(math.atan2(T[1] - S[1], T[0] - S[0]))
    A('<g class="layer" data-layer="reach">')
    A(f'<path class="f-rep" d="M{pt(r0)} A{f(R)} {f(R)} 0 0 1 {pt(r1)}" fill="none" stroke="{C["blue"]}" stroke-width="1.4" stroke-dasharray="2 5" stroke-linecap="round"/>')
    A(label(r0[0] + 10, r0[1] + 12, "reach limit, r = l₁ + l₂", rep=True))
    A(f'<path id="fig-manip-fill" class="f-wash" d="{ellipse_d(T, 7, 24, rad)}" fill="{C["wash"]}"/>')
    A(f'<path id="fig-manip" class="f-rep" d="{ellipse_d(T, 7, 24, rad)}" fill="none" stroke="{C["blue"]}" stroke-width="1.3"/>')
    A(label(400, 248, "manipulability", rep=True))
    A('</g>')

    # ---- scene geometry (context, always on) ----------------------------------
    A(f'<g class="scene" fill="{C["surface"]}" stroke="{C["ink"]}" stroke-width="2" stroke-linejoin="round">')
    A(f'<rect class="f-body" x="520" y="150" width="152" height="{GROUND - 150}"/>')
    A(f'<rect class="f-body2" x="514" y="141" width="164" height="10" rx="2" fill="{C["surface2"]}"/>')
    for y0, h in ((244, 70), (322, 62)):
        m = y0 + h / 2
        A(f'<rect class="f-body" x="512" y="{y0}" width="8" height="{h}"/>')
        A(f'<path class="f-ink" d="M512 {f(m - 6)} L504 {f(m - 2)} M512 {f(m + 6)} L504 {f(m + 2)}" fill="none" stroke-width="2"/>')
        A(f'<circle class="f-inkfill" cx="502" cy="{f(m)}" r="3.2" fill="{C["ink"]}" stroke="none"/>')
    A(f'<rect class="f-hidden" x="520" y="170" width="118" height="58" fill="none" stroke="{C["muted"]}" stroke-width="1.2" stroke-dasharray="5 4"/>')
    A(f'<g id="fig-drawer" transform="translate({f(fx - 482)} 0)">')
    A(f'<rect class="f-body2" x="490" y="170" width="30" height="58" fill="{C["surface2"]}" stroke-width="1.6"/>')
    A('<rect class="f-body" x="482" y="162" width="8" height="74"/>')
    A('<path class="f-ink" d="M482 199 L472 203.5 M482 213 L472 208.5" fill="none" stroke-width="2.2"/>')
    A(f'<circle class="f-inkfill" cx="470" cy="206" r="3.6" fill="{C["ink"]}" stroke="none"/>')
    A('</g>')
    A('</g>')

    # ---- robot geometry --------------------------------------------------------
    A('<g class="layer" data-layer="geometry">')
    A(f'<g class="f-far" fill="none" stroke="{C["far"]}" stroke-width="13" stroke-linecap="round" stroke-linejoin="round">')
    for hip, knee, foot in ((H1, K1, F1), (H2, K2, F2)):
        A(f'<path d="M{hip[0] + 18} {hip[1] - 4} L{knee[0] + 18} {knee[1] - 4} L{foot[0] + 18} {foot[1]}"/>')
    A('</g>')
    A(f'<path class="f-body" d="M122 196 H322 L347 216 L337 240 H116 L100 218 Z" fill="{C["surface"]}" stroke="{C["ink"]}" stroke-width="2.4" stroke-linejoin="round"/>')
    A(f'<path class="f-ink" d="M128 207 H318" fill="none" stroke="{C["ink"]}" stroke-width="1" opacity="0.35"/>')
    A(f'<rect class="f-inkfill" x="336" y="208" width="7" height="12" rx="2" fill="{C["ink"]}"/>')

    def capsule(a, b, w, ids=None):
        i1 = f' id="{ids}-o"' if ids else ""
        i2 = f' id="{ids}-i"' if ids else ""
        A(f'<line{i1} class="f-cap-out" x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}" stroke="{C["ink"]}" stroke-width="{w + 4}" stroke-linecap="round"/>')
        A(f'<line{i2} class="f-cap-in" x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}" stroke="{C["surface"]}" stroke-width="{w}" stroke-linecap="round"/>')

    for hip, knee, foot in ((H1, K1, F1), (H2, K2, F2)):
        capsule(knee, foot, 8)
        capsule(hip, knee, 19)
        A(f'<circle class="f-inkfill" cx="{foot[0]}" cy="{foot[1]}" r="8" fill="{C["ink"]}"/>')
        A(f'<circle class="f-body" cx="{knee[0]}" cy="{knee[1]}" r="8.5" fill="{C["surface"]}" stroke="{C["ink"]}" stroke-width="2"/>')
        A(f'<circle class="f-body" cx="{hip[0]}" cy="{hip[1]}" r="13" fill="{C["surface"]}" stroke="{C["ink"]}" stroke-width="2"/>')
    A(f'<rect class="f-body" x="268" y="177" width="32" height="20" rx="5" fill="{C["surface"]}" stroke="{C["ink"]}" stroke-width="2"/>')
    capsule(S, E, 13, "fig-a1")
    capsule(E, W, 11, "fig-a2")
    A(f'<circle class="f-body" cx="{f(S[0])}" cy="{f(S[1])}" r="9.5" fill="{C["surface"]}" stroke="{C["ink"]}" stroke-width="2"/>')
    A(f'<circle id="fig-elbow" class="f-body" cx="{f(E[0])}" cy="{f(E[1])}" r="9" fill="{C["surface"]}" stroke="{C["ink"]}" stroke-width="2"/>')
    A(f'<g id="fig-gripper" transform="translate({pt(W)})">')
    A(f'<path class="f-body" d="M-4 -9 H20 L25 -5 V5 L20 9 H-4 Z" fill="{C["surface"]}" stroke="{C["ink"]}" stroke-width="2" stroke-linejoin="round"/>')
    A(f'<path class="f-ink" d="M24 -5 Q33 -8 38 -3.8 M24 5 Q33 8 38 3.8" fill="none" stroke="{C["ink"]}" stroke-width="3" stroke-linecap="round"/>')
    A(f'<circle class="f-body" cx="0" cy="0" r="7" fill="{C["surface"]}" stroke="{C["ink"]}" stroke-width="2"/>')
    A('</g>')
    A('</g>')

    # ---- dynamics: mass, inertia, actuation limits ---------------------------
    cx, cy = COM
    A('<g class="layer" data-layer="dynamics">')
    A(f'<ellipse class="f-rep" cx="{f(cx)}" cy="{f(cy)}" rx="84" ry="21" fill="none" stroke="{C["blue"]}" stroke-width="1.2" stroke-dasharray="6 4"/>')
    A(f'<circle class="f-body" cx="{f(cx)}" cy="{f(cy)}" r="9" fill="{C["surface"]}" stroke="{C["ink"]}" stroke-width="1.6"/>')
    A(f'<path class="f-inkfill" d="M{f(cx)} {f(cy)} V{f(cy - 9)} A9 9 0 0 1 {f(cx + 9)} {f(cy)} Z M{f(cx)} {f(cy)} V{f(cy + 9)} A9 9 0 0 1 {f(cx - 9)} {f(cy)} Z" fill="{C["ink"]}"/>')
    A(leader(f"M{f(cx - 7)} {f(cy + 8)} L234 254 H222"))
    A(label(186, 258, "m, I"))
    kx, ky = K2
    rg = 21
    g0, g1 = math.radians(128), math.radians(232)
    p0 = (kx + rg * math.cos(g0), ky + rg * math.sin(g0))
    p1 = (kx + rg * math.cos(g1), ky + rg * math.sin(g1))
    A(f'<path class="f-rep" d="M{pt(p0)} A{rg} {rg} 0 0 1 {pt(p1)}" fill="none" stroke="{C["blue"]}" stroke-width="2"/>')
    for k in range(5):
        t = math.radians(128 + k * 26)
        a_ = (kx + (rg - 4) * math.cos(t), ky + (rg - 4) * math.sin(t))
        b_ = (kx + (rg + 4) * math.cos(t), ky + (rg + 4) * math.sin(t))
        A(f'<line class="f-rep" x1="{f(a_[0])}" y1="{f(a_[1])}" x2="{f(b_[0])}" y2="{f(b_[1])}" stroke="{C["blue"]}" stroke-width="1.2"/>')
    A(f'<path class="f-rep" d="{arrowhead(p1, math.degrees(g1) + 90, 7)}" fill="none" stroke="{C["blue"]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
    A(label(158, 318, "|τ| ≤ τ_max", rep=True))
    A('</g>')

    # ---- kinematic graph ---------------------------------------------------------
    A('<g class="layer" data-layer="graph">')
    A(f'<g class="f-rep" fill="none" stroke="{C["blue"]}" stroke-width="2" stroke-linecap="round">')
    for a, b in [(B, H1), (B, H2), (B, S), (H1, K1), (K1, F1), (H2, K2), (K2, F2)]:
        A(f'<line x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}"/>')
    A(f'<line id="fig-e1" x1="{f(S[0])}" y1="{f(S[1])}" x2="{f(E[0])}" y2="{f(E[1])}"/>')
    A(f'<line id="fig-e2" x1="{f(E[0])}" y1="{f(E[1])}" x2="{f(W[0])}" y2="{f(W[1])}"/>')
    A(f'<line id="fig-e3" x1="{f(W[0])}" y1="{f(W[1])}" x2="{f(T[0])}" y2="{f(T[1])}"/>')
    A('</g>')
    A(f'<g class="f-node" fill="{C["surface"]}" stroke="{C["blue"]}" stroke-width="2.2">')
    for n in (H1, K1, F1, H2, K2, F2, S):
        A(f'<circle cx="{f(n[0])}" cy="{f(n[1])}" r="5.5"/>')
    A(f'<circle id="fig-nE" cx="{f(E[0])}" cy="{f(E[1])}" r="5.5"/>')
    A(f'<circle id="fig-nW" cx="{f(W[0])}" cy="{f(W[1])}" r="5.5"/>')
    A(f'<circle id="fig-nT" cx="{f(T[0])}" cy="{f(T[1])}" r="4.5"/>')
    A('</g>')
    A(f'<rect class="f-repfill" x="{f(B[0] - 7)}" y="{f(B[1] - 7)}" width="14" height="14" fill="{C["blue"]}"/>')
    A(leader(f"M{f(E[0] - 8)} {f(E[1] - 6)} L336 104 H300"))
    A(label(206, 100, "kinematic graph"))
    A(label(206, 113, "joints = nodes", dim=True))
    A('</g>')

    # ---- scene kinematics: virtual kinematic chain ---------------------------
    wx, wy = WORLD
    A('<g class="layer" data-layer="scene">')
    A(f'<path class="f-ink" d="M{wx} {wy} H{wx + 30} M{wx} {wy} V{wy - 30}" fill="none" stroke="{C["ink"]}" stroke-width="1.8"/>')
    A(f'<path class="f-ink" d="{arrowhead((wx + 31, wy), 0, 6)} {arrowhead((wx, wy - 31), -90, 6)}" fill="none" stroke="{C["ink"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>')
    A(label(wx - 6, wy + 18, "world"))
    c0, c1, c2, c3 = (wx, wy), (wx - 6, 262), (112, 170), B
    A(f'<path class="f-rep" d="M{pt(c0)} C {pt(c1)}, {pt(c2)}, {pt(c3)}" fill="none" stroke="{C["blue"]}" stroke-width="1.8" stroke-dasharray="7 5"/>')

    def bez(t):
        u = 1 - t
        return (u**3 * c0[0] + 3*u*u*t * c1[0] + 3*u*t*t * c2[0] + t**3 * c3[0],
                u**3 * c0[1] + 3*u*u*t * c1[1] + 3*u*t*t * c2[1] + t**3 * c3[1])
    for t, name, kind in ((0.18, "x", "p"), (0.36, "y", "p"), (0.54, "θ", "r")):
        q_ = bez(t)
        if kind == "p":
            A(f'<rect class="f-node" x="{f(q_[0] - 5)}" y="{f(q_[1] - 5)}" width="10" height="10" fill="{C["surface"]}" stroke="{C["blue"]}" stroke-width="2"/>')
        else:
            A(f'<circle class="f-node" cx="{f(q_[0])}" cy="{f(q_[1])}" r="5.5" fill="{C["surface"]}" stroke="{C["blue"]}" stroke-width="2"/>')
        A(label(q_[0] - 20, q_[1] + 4, name, rep=True))
    A(label(18, 176, "virtual base joints", rep=True))
    A(label(18, 189, "(VKC)", rep=True, dim=True))
    A(f'<line id="fig-chain" class="f-rep" x1="{f(T[0])}" y1="{f(T[1])}" x2="{f(P[0])}" y2="{f(P[1])}" stroke="{C["blue"]}" stroke-width="1.8" stroke-dasharray="7 5"/>')
    A(f'<path class="f-rep" d="M{f(P[0] - 34)} {f(P[1])} H{f(P[0] + 34)}" fill="none" stroke="{C["blue"]}" stroke-width="1.4"/>')
    A(f'<path class="f-rep" d="{arrowhead((P[0] - 35, P[1]), 180, 6)} {arrowhead((P[0] + 35, P[1]), 0, 6)}" fill="none" stroke="{C["blue"]}" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>')
    A(f'<rect class="f-repfill" x="{f(P[0] - 6)}" y="{f(P[1] - 6)}" width="12" height="12" fill="{C["blue"]}"/>')
    A(leader(f"M{f(P[0])} {f(P[1] - 8)} V124 H604"))
    A(label(560, 98, "prismatic", rep=True, dim=True))
    A(label(560, 112, "drawer joint q_d", rep=True))
    A('</g>')

    # ---- contact and stability (top, so the grasp ring sits over the graph) --
    feet = [F1[0], F2[0], F1[0] + 18, F2[0] + 18]
    A('<g class="layer" data-layer="contact">')
    A(f'<line class="f-maize" x1="{min(feet)}" y1="{GROUND + 4}" x2="{max(feet)}" y2="{GROUND + 4}" stroke="{C["maize"]}" stroke-width="6" stroke-linecap="round"/>')
    A(f'<line class="f-lead" x1="{f(cx)}" y1="{f(cy + 10)}" x2="{f(cx)}" y2="{GROUND - 3}" stroke="{C["ink2"]}" stroke-width="1.1" stroke-dasharray="3 3"/>')
    A(f'<path class="f-leadfill" d="M{f(cx)} {GROUND - 1} l-5 -8 h10 Z" fill="{C["ink2"]}"/>')
    for fxp, name in ((F1[0], "f₁"), (F2[0], "f₂")):
        A(f'<line class="f-rep" x1="{fxp + 12}" y1="{GROUND - 2}" x2="{fxp + 12}" y2="{GROUND - 40}" stroke="{C["blue"]}" stroke-width="1.8"/>')
        A(f'<path class="f-rep" d="{arrowhead((fxp + 12, GROUND - 41), -90, 7)}" fill="none" stroke="{C["blue"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>')
        A(label(fxp + 18, GROUND - 30, name, rep=True))
    A(label(min(feet) + 8, GROUND + 24, "support polygon · CoM projection"))
    A('<g id="fig-grasp">')
    A(f'<circle class="f-maize" cx="{f(bar)}" cy="206" r="8.5" fill="none" stroke="{C["maize"]}" stroke-width="3"/>')
    A(leader(f"M{f(bar - 5)} 198 L{f(bar - 16)} 170 H{f(bar - 44)}"))
    A(label(bar - 88, 174, "grasp"))
    A('</g>')
    A('</g>')

    A('</svg>')
    return "\n".join(o)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "hero.svg").write_text(build(True))
    if "--site" in sys.argv:
        (ROOT / "_includes" / "figure-body.html").write_text(build(False) + "\n")
    print("pose(q0):", {k: (tuple(round(x, 1) for x in v) if isinstance(v, tuple) else v) for k, v in pose(Q0).items()})
