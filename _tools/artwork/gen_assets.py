"""Favicon, touch icon and social preview image (needs ImageMagick).

  python3 gen_assets.py   -> assets/img/favicon.svg, favicon-32.png, apple-touch-icon.png, og-image.png
"""
import pathlib
import re
import subprocess

import gen_hero

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out"
IMG = HERE.parents[1] / "assets" / "img"

MARK = """<g fill="none" stroke="{links}" stroke-linecap="round" stroke-linejoin="round" stroke-width="3.2">
    <path d="M11.5 25 L8.5 32.5 L11.5 40"/>
    <path d="M28.5 25 L25.5 32.5 L28.5 40"/>
    <path d="M27 20 L32 10.5 L39.5 14.5"/>
  </g>
  <path d="M10 19.5 H30.5 L33.5 22.5 L31 26 H9.5 L7.5 22.5 Z" fill="{links}" stroke="{links}" stroke-width="1" stroke-linejoin="round"/>
  <g fill="{bg}" stroke="{joint}" stroke-width="2.4">
    <circle cx="8.5" cy="32.5" r="2.7"/><circle cx="25.5" cy="32.5" r="2.7"/><circle cx="32" cy="10.5" r="2.7"/>
  </g>
  <circle cx="40" cy="14.8" r="3.6" fill="#FFCB05"/>"""


def favicon(rx=11):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">'
            f'<rect width="48" height="48" rx="{rx}" fill="#0C1B2E"/>'
            + MARK.format(links="#FFFFFF", bg="#0C1B2E", joint="#8DB4FF") + "</svg>\n")


def og_image():
    W, H = 1200, 630
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
         f'<rect width="{W}" height="{H}" fill="#F2F4F7"/>']
    for x in range(0, W + 1, 24):
        o.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="#E2E6EC" stroke-width="1"/>')
    for y in range(0, H + 1, 24):
        o.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="#E2E6EC" stroke-width="1"/>')
    # figure panel
    o.append('<rect x="572" y="92" width="590" height="406" rx="14" fill="#FFFFFF" stroke="#D9DFE7" stroke-width="2"/>')
    fig = gen_hero.build(True)
    inner = fig.split("\n", 2)[2].rsplit("</svg>", 1)[0]          # drop <svg> and background rect
    inner = re.sub(r'<text class="f-label[^"]*"[^>]*>[^<]*</text>', "", inner)
    inner = re.sub(r'<path class="f-lead f-leader"[^>]*/>', "", inner)
    o.append(f'<g transform="translate(584 110) scale(0.785)">{inner}</g>')
    # mark + words
    o.append('<g transform="translate(64 64) scale(1.6)">'
             + MARK.format(links="#0C1B2E", bg="#F2F4F7", joint="#1A5FD6").replace('fill="#FFCB05"', 'fill="#FFCB05" stroke="#0C1B2E" stroke-width="1.4"')
             + "</g>")
    o.append('<text x="64" y="200" font-family="Noto Sans Mono" font-size="17" fill="#5B6A7D">READING GROUP · UNIVERSITY OF MICHIGAN</text>')
    o.append('<text x="60" y="288" font-family="Lato" font-weight="900" font-size="70" fill="#0C1B2E">Embodiment</text>')
    o.append('<text x="60" y="362" font-family="Lato" font-weight="900" font-size="70" fill="#0C1B2E">Reading Group</text>')
    o.append('<text x="64" y="428" font-family="Lato" font-weight="400" font-style="normal" font-size="25" fill="#33445A">How robots represent their own bodies,</text>')
    o.append('<text x="64" y="462" font-family="Lato" font-weight="400" font-style="normal" font-size="25" fill="#33445A">and what that unlocks for planning,</text>')
    o.append('<text x="64" y="496" font-family="Lato" font-weight="400" font-style="normal" font-size="25" fill="#33445A">control and skills.</text>')
    o.append('<circle cx="72" cy="566" r="7" fill="#FFCB05" stroke="#0C1B2E" stroke-width="1.5"/>')
    o.append('<text x="90" y="572" font-family="Noto Sans Mono" font-size="18" fill="#0C1B2E">Fridays · FRB + Zoom · papers and a monthly Tooling Hour</text>')
    o.append(f'<rect x="0" y="{H - 8}" width="{W}" height="8" fill="#0C1B2E"/>')
    o.append("</svg>")
    return "\n".join(o)


def png(svg_path, out, size=None, density=96):
    cmd = ["convert", "-background", "none", "-density", str(density), str(svg_path)]
    if size:
        cmd += ["-resize", f"{size}x{size}"]
    cmd.append(str(out))
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    (IMG / "favicon.svg").write_text(favicon())
    OUT.mkdir(exist_ok=True)
    sq = OUT / "icon-square.svg"
    sq.write_text(favicon(rx=0))
    png(IMG / "favicon.svg", IMG / "favicon-32.png", 32, density=192)
    png(sq, IMG / "apple-touch-icon.png", 180, density=1152)
    og = OUT / "og.svg"
    og.write_text(og_image())
    subprocess.run(["convert", "-density", "96", str(og), "-flatten", "-strip", str(IMG / "og-image.png")], check=True)
    print("ok")
