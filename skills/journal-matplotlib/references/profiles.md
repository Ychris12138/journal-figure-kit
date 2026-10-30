# Mode profiles and export

Centralize dimensions, text, lines, colors, mappings and normalization at the top of generated code. Use `mpl.rc_context` and keep scripts self-contained.

```python
BASE_RC = {
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.linewidth': 0.6, 'lines.linewidth': 1.0,
    'xtick.major.width': 0.6, 'ytick.major.width': 0.6,
    'legend.frameon': False,
    'pdf.fonttype': 42, 'ps.fonttype': 42, 'svg.fonttype': 'none',
    'savefig.bbox': None, 'savefig.facecolor': 'white',
}
```

These are local defaults, not universal journal requirements. Keep top/right spines where the scientific plot benefits from them. Check font availability rather than silently claiming Arial was used. Math font and Unicode glyphs also need inspection.

| Mode | Working text | Export |
|---|---|---|
| explore | Choose for screen | PNG 180 dpi |
| report | Start near 9 pt, adapt to report | PDF + PNG 300 dpi |
| publication | Use the selected journal entry; no global 8 pt rule | PDF + PNG 600 dpi, with journal-specific additional exports |

Read [journals.md](journals.md) before assigning publication dimensions or fonts. Without a named journal, a user-approved custom size is valid; do not imply that 3.5/7.2 inches is a universal column width. A journal minimum is a lower bound, not a preferred working font size. Use `(a)` for APS/AIP; Nature final labels use bold upright `a`; unresolved journal label rules remain explicit choices.

For journal font presets and one-place adjustments, use [typography.md](typography.md). Its role sizes are specified at manuscript placement size; use its `rc()` plus post-draw `apply()` so explicitly sized legends/annotations/colorbars do not escape a global adjustment. Record final placement width separately from a larger working canvas. The example below already uses the final canvas; it needs no reduction compensation.

```python
from pathlib import Path
import matplotlib as mpl
import matplotlib.pyplot as plt

width_mm, height_mm = 89, 65  # Nature FINAL single-column example, not universal
png_dpi = 600
with mpl.rc_context({**BASE_RC, 'font.size': 7}):
    fig, ax = plt.subplots(figsize=(width_mm / 25.4, height_mm / 25.4),
                           layout='constrained')
    fig.get_layout_engine().set(w_pad=2 / 72, h_pad=2 / 72)
    # Read plot-palette.json exported by palette_cards.py after confirmation.
    # Draw source data using that mapping and its background/band/normalization roles.
    fig.canvas.draw()
    stem = Path('figure')
    fig.savefig(stem.with_suffix('.pdf'), dpi=png_dpi, bbox_inches=None)
    fig.savefig(stem.with_suffix('.png'), dpi=png_dpi, bbox_inches=None)
```

PDF DPI controls rasterized layers, not vector text/lines. Source image pixels still determine effective resolution. Save formats from the same live figure/configuration. Export standalone panels by calling the same data-panel drawing function with a new layout. Close figures after exports/QA.

Publication contract example (adapt; never invent approval):

```json
{
  "journal": "Nature", "stage": "final", "role": "main",
  "size_mm": [89, 65],
  "source": {
    "url": "https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels/",
    "locator": "Figure sizing", "checked": "YYYY-MM-DD"
  },
  "palette": {"card_id": "B", "revision": 1, "fingerprint": null},
  "confirmation": {"status": "pending", "evidence": null, "scope": null},
  "mapping": {},
  "normalization": null,
  "source_data": [], "script": "plot.py",
  "qa": {"png_viewed": false, "pdf_viewed": false, "warnings": []}
}
```

For numeric color, record cmap name, norm class, vmin/vmax, midpoint (if any), masking and extension policy. Keep real data paths and hashes where practical; do not duplicate large trajectory files just to deliver a figure.

Populate the palette/mapping/confirmation fields from the approved export; the example deliberately contains no fabricated approval. See [palette-cards.md](palette-cards.md). When a user supplies a reference image, record the observed samples and adapted proposal separately, then wait for the new card confirmation before recoloring actual data.
