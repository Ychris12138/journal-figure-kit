# Typography at manuscript placement size

Read for publication plots, reduced figures, changing journal, or any request to make text larger. Use the size **after placement in the manuscript**, not the figure window, browser zoom, DPI, or points in an oversized source file.

For uniform placement, `final_pt = canvas_pt × final_width_mm / canvas_width_mm`. An 180 mm source with 8 pt text placed at 90 mm has 4 pt text. Either rebuild at 90 mm with 8 pt text (preferred), or use 16 pt on the 180 mm canvas and audit the other scaled marks. Increasing PNG DPI does not change this ratio. Never stretch width and height independently. Measure a combined multipanel as one whole figure; standalone panels get their own final size and the same intended final body size.

## Built-in working choices

These are **our readable starting points**, not survey averages or publisher mandates. All numbers are final-placement points. Detailed sources, locators, access status and values live in [typography-presets.json](typography-presets.json); sizing/stage/role rules remain in [journals.md](journals.md). TOC and extended-data figures need their separate guide.

| Journal | Axes / titles / colorbar labels | Ticks / legend / annotations / offsets | Panels | Evidence boundary |
|---|---:|---:|---:|---|
| Nature | 7 | 7 | 8 bold lowercase | Official body 5–7; panel 8 exception |
| Nature Communications (`nc`) | 8 | 8 | 8 bold lowercase | 2019 official optimum 5–8; recheck current rules |
| PRL / PRE (separate selections) | 9 | 9 | 10, `(a)` | APS ≥2 mm actual lettering height; 9 pt is only a starting point |
| JCP | 9 | 8.5 | 10, `(a)` | AIP minimum 8 pt; do not transfer another AIP title's recommendation |
| JPCL | 8 | 8 | 9 | ACS minimum 4.5 pt; we do not aim at the lower bound |
| PNAS | 9 | 8 | 10 | 6–12 pt from prior verified record; live access failed 2026-10-30 |
| Science | 8 | 8 | 9 | Local draft choice; current official font limits unverified |

Caption paragraphs outside the artwork belong to manuscript typography. A font point is an em size, not capital height/x-height; 2 mm of ink is **not** a 5.67 pt font. For APS inspect representative letters/numbers, including math, at final size. A Text bounding box includes font metrics and cannot prove ink height. Family/fallback can change readability at identical points. Do not infer a journal-wide average from a small sample; outlined/raster text cannot yield exact original points by PDF extraction.

## Convenient controls

Use one `FontPlan` near the top of the user's plot script. It changes sizes only, apart from tagged panel weight/style; family, data, colors, lines, aspect and canvas remain intact. Use `mpl.rc_context`, apply after building all artists, and repeat after changed text or limits. Repeated application is absolute and does not accumulate scaling.

```python
from typography import resolve_typography, tag_text

fonts = resolve_typography(
    'jcp', final_width_mm=85,
    font_scale=1.0,              # “全部字大 10%” -> 1.10
    # body_pt=10,               # “正文基准设为 10 pt”
    overrides={'legend': 9},    # exact FINAL pt; overrides win
)
with mpl.rc_context({**BASE_RC, **fonts.rc()}):
    fig, ax = plt.subplots(figsize=(85/25.4, 65/25.4), layout='constrained')
    # Draw approved data/colors. cb = fig.colorbar(...)
    tag_text(ax.text(-.12, 1.04, '(a)', transform=ax.transAxes), 'panel')
    record = fonts.apply(fig)   # pass colorbars=[cb] if present
    # Reflow GridSpec/legend/margins when bigger text crowds content.
    export_pair(fig, stem, width_mm=85, height_mm=65,
                provenance={'typography': record})
```

The API is available when the skill's scripts directory is on `sys.path`. For a self-contained user project, copy the helper and JSON preserving relative structure, or resolve once and copy the explicit role sizes into the project. Do not depend on an undisclosed personal skill path.

Precedence: journal defaults → proportional `body_pt` adjustment → `font_scale` → absolute role overrides. Roles: `body`, `label`, `tick`, `legend`, `legend_title`, `annotation`, `colorbar_label`, `colorbar_tick`, `panel`, `title`, `offset`. Direct artist `fontsize` values are replaced by `apply`; tag semantic exceptions and set role overrides. Untagged free text/table-cell text is annotation. Panel letters are never guessed from their string; tag them and choose (a)/a/A explicitly. Table-cell geometry is not rearranged by this helper.

For an inherited 170 mm canvas placed at 85 mm, add `canvas_width_mm=170`; working sizes double. This compensates **text only**. Rebuilding at final size is preferred because line widths, markers, gaps and raster detail otherwise also need checks. Do not force a dense wide figure into one column just because fonts can be enlarged; split panels or change layout when necessary.

Map natural requests directly: “整体字号放大 10%”, “图例 9 pt、刻度 8 pt”, “按 JCP 单栏重排，字大一些”. Reuse explicit preferences instead of resetting each call. Typography-only edits reuse palette approval. If an override conflicts with a journal bound, report it and preserve the requested value; do not silently clamp or claim compliance. Nature 7 pt × 1.2 exceeds the main-body maximum. A draft and a journal-sized alternative can make the tradeoff visible. A minimum is not a target, and a maximum still matters.

## Inspect the placed result

```text
python scripts/typography.py --journal jcp --final-width-mm 85 --font-scale 1.1 --set legend=9 --output typography.json
python scripts/audit_placement.py figure.pdf --final-width-mm 85 --min-font-pt 8 --json placed-fonts.json
```

`audit_placement.py` reads only the figure, measures extracted PDF span sizes under uniform width placement, and reports effective dimensions/font distribution. Exit 1 means review warnings; 2 means invalid input/dependency failure. No extractable text is a warning, not a pass. Math scripts can correctly be smaller; inspect them separately. Panel exceptions make a global upper bound insufficient. This cannot see raster/outlined text, prove ink height, or infer Word/LaTeX's actual placement width.

Export a physical-size proof or insert the PDF at the agreed width. Verify at 100% print scale; “fit to window” is not a physical-size view. Inspect PNG and a separately rendered PDF for ticks, legend, colorbar, long units, scripts, overlap and clipping. Larger text often needs more height, fewer redundant ticks or an external legend, not automatic font shrinking. Record canvas/final width, reduction, role sizes, source status and warnings in provenance. Optional 75%/50% stress proofs must be distinguished from intended final placement.

After every font adjustment, run [collision screening](collisions.md). Reflow or reposition around the selected fonts; do not shrink them back silently to satisfy layout checks.
