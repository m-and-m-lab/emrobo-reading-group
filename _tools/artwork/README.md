# Artwork generators

The home page diagram and the icons are generated so their geometry stays
consistent. Jekyll ignores this folder.

```bash
python3 _tools/artwork/gen_hero.py --site     # -> _includes/figure-body.html
python3 _tools/artwork/gen_assets.py          # -> assets/img/ favicon, touch icon, social image (needs ImageMagick)
```

Standalone previews land in `_tools/artwork/out/` (git-ignored); render one
with `convert -density 96 out/hero.svg hero.png`.
