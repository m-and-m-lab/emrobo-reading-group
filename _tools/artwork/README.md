# Artwork generators

The figure on the home page, the paper glyphs and the icons are generated so
their geometry stays consistent (the figure's drawer animation in
`assets/js/site.js` uses the same arm lengths and inverse kinematics as
`gen_hero.py`). Jekyll ignores this folder.

```bash
python3 _tools/artwork/gen_hero.py --site     # -> _includes/figure-body.html
python3 _tools/artwork/gen_glyphs.py --site   # -> _includes/glyphs/*.html
python3 _tools/artwork/gen_assets.py          # -> assets/img/ (needs ImageMagick)
```

Standalone previews land in `_tools/artwork/out/` (git-ignored); render one
with `convert -density 96 out/hero.svg hero.png`.

To add a glyph for a new paper, write a function in `gen_glyphs.py`, register
it in `GLYPHS`, regenerate, and set `glyph:` on the paper in `_data/papers.yml`.
