# Prevent and repair figure collisions

Read after choosing the final size and typography, and after changing fonts, labels, ticks, legends or panels. Check both decoration-to-decoration collisions and decoration-to-data obstruction. An opaque legend can hide the evidence of its own collision; looking only at the final bitmap or at data vertices is insufficient.

## Construction presets

[layout-presets.json](layout-presets.json) contains local mode thresholds and scene choices, not journal requirements. Publication screening starts with 0.4 mm clearance between decoration boxes and data; report 0.3 mm, explore 0.15 mm. Adjust a threshold only with a recorded reason. Use the final physical canvas from the typography plan; a larger working canvas scales these clearances on placement.

| Scene | Start with | Repair if crowded |
|---|---|---|
| Sparse line / fit | Inside legend only after checking actual data ink | Try a finite set of clear positions; otherwise reserve a legend cell |
| Dense bars / scatter / ribbons | Dedicated legend row/column | Adjust GridSpec ratios or figure height within the size contract |
| Heatmap / physical image | Dedicated colorbar cell, preserved aspect and norm | Move colorbar/labels; explicit in-cell numeric overlays stay in their cells |
| Multiple panels | GridSpec, aligned outer labels, shared key only when identities agree | Reflow row/column spacing; check labels entering neighboring axes |
| Long category names / units | Complete labels, sufficient label space | Wrap whole labels; moderate rotation if needed; retain values/units |
| Fit equations / free notes | Empty area or separate note cell | Move only free axes-coordinate notes; preserve every word and number |
| Point-linked annotations | Fixed scientific targets with leader lines | Reposition text while preserving targets; review line crossings separately |

Call `constrained_layout` before drawing and retain one layout engine. A later `tight_layout()` disables it. A bare `bbox_to_anchor` outside the axes does not itself reserve space; a real GridSpec row/column is predictable. Figure-level `outside ...` legend locations can work with current Matplotlib constrained layout, but are version-sensitive and still need export checks. `bbox_inches='tight'` is not a repair for a fixed journal-size contract.

Do not hide data, shorten scientific labels without checking their meaning, deduplicate different series by identical legend text, change axis limits/normalization, flatten physical aspect, or reduce approved fonts to make a check pass. A white box over a curve hides it rather than resolving the conflict. Meaningful missing-data gaps remain gaps.

## Render-time audit

```python
from layout_audit import audit_layout, save_overlay, write_audit
audit = audit_layout(fig, mode='publication')
write_audit(audit, 'figure.layout.json')
save_overlay(fig, audit, 'figure.layout-review.png')  # diagnostic only
```

The audit renders on Agg at the current figure DPI, freezes the layout temporarily, and measures whole text and legend boxes. It separately renders visible data layers with the decorations/backgrounds hidden, so curves behind opaque legends remain detectable. The temporary visibility, canvas and layout engine are restored even on failure. It includes lines, marker extents, bars, bands, error bars, meshes and images. It does not treat an entire curve's bounding rectangle as occupied, so a NaN gap is not filled artificially. No source data or styling values are changed.

Findings identify the items and pixel boxes: `off_canvas`, `text_clipped`, `decoration_overlap`, `decoration_clearance`, `data_overlap`, `data_clearance`, `neighbor_axes_intrusion`, `spine_crossing`. Out-of-view ticks are excluded. Whole multiline boxes can include empty space, and thin/very transparent ink can be missed at low render DPI. This is conservative screening, not a glyph-level collision certificate. For dense/thin figures audit at a suitably detailed working render and inspect the actual exported PNG and rendered PDF. PDF font/backend geometry can differ from Agg. Raster/outlined text inside a source image is not separate text to this checker.

Tables, custom artists, nonrectilinear axes and annotation leader paths trigger manual-review scope notes; nested or hidden-parent structures and custom clipping require care. No issue count alone proves all such objects were checked. Keep `skipped` and `limitations` in the report.

## Bounded repair

```python
from layout_audit import reflow_layout, place_legend, place_axes_note

reflow = reflow_layout(fig, mode='publication')
legend_repair = place_legend(ax)       # current Axes legend; up to 9 candidates
note_repair = place_axes_note(note)   # free text with transform=ax.transAxes
audit = audit_layout(fig)
```

`reflow_layout` handles ordinary subplot/GridSpec decoration spacing at the existing canvas size and fonts. It refuses a different active layout engine or manual/inset axes rather than silently replacing that geometry. It cannot guarantee enough room in an overfilled canvas. Fix that source layout deliberately and rerender.

`place_legend` keeps handles, order, labels, styling and size. It keeps an already-clear legend. Candidate positions must clear the legend's findings without increasing the total findings. If none works, it restores the original location/anchor and returns `needs_reserved_region`. Do not run it for a position the user explicitly locked; report the conflict instead. It checks the current Axes legend; manually added extra legends and figure legends need explicit arrangement. It never moves a legend off-page hoping that a later crop will save it.

`place_axes_note` applies the same bounded search to free notes, retaining font/text. It refuses `Annotation` and data-coordinate text to avoid breaking scientific target identities. Move anchored text explicitly with its leader line, not by changing target coordinates. Optional [adjustText](https://adjusttext.readthedocs.io/en/latest/) can help dense point-label sets only after final geometry, one axes at a time, with fixed targets, bounded iterations, `expand_axes=False` and no silently dropped labels; it is not a bundled dependency or tested auto-fix here. Reaudit and inspect arrows afterwards.

For a reserved legend, create the cell before data plotting:

```python
from layout_audit import reserved_legend
fig = plt.figure(figsize=(89/25.4, 75/25.4), layout='constrained')
grid = fig.add_gridspec(2, 1, height_ratios=[1, .18])
ax = fig.add_subplot(grid[0])
key = fig.add_subplot(grid[1])
# Draw data and collect explicit handles in scientific order.
legend = reserved_legend(key, handles, labels, frameon=False, ncols=2)
```

The helper rejects a key axes containing data and preserves duplicate label strings; identities come from the explicit handles, not inferred text equality. If keys need more room, increase the reserved row/column or reorganize the panel, then check final fonts and limits again.

## Intentional overlays and delivery

```python
from layout_audit import allow_data_overlay
allow_data_overlay(cell_text, 'Numeric value of this heatmap cell')
```

Only explicit, reasoned Text overlays can bypass data-overlap findings. Text-text collisions, clipping and canvas checks remain active. Do not blanket-exempt an axes or a covering legend. In-cell values must match the actual source cell; white/black text contrast remains a separate check. A deliberate inset may still need manual review of parent-panel occlusion.

`export_pair` now records `collision_audit` automatically. Its default `collision_mode='warn'` exports the reviewable draft with findings; `collision_mode='error'` refuses export while any finding or skipped scope remains; `'off'` explicitly records a skipped check. Strict refusal does not write a new PDF/PNG pair. A manual disposition of a conservative warning must remain documented in provenance; do not falsify a screen pass. Existing `layout_warnings` retain the earlier off-canvas check.

Use a targeted loop: identify the colliding items → fix their owning layout or placement → redraw and rerun the failed checks → review PNG and rendered PDF. Stop after at most three repair rounds; unresolved conflicts need a different composition or explicit recorded disposition. No indefinite nudging, automatic cropping or repeated font shrinking. Run again after typography edits and for every standalone panel; overview clearance does not guarantee standalone clearance.
