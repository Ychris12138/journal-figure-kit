# Standalone panel exports

Apply whenever a figure contains multiple data-bearing panels. Produce the overview and standalone versions in the same run; do not wait for a separate request.

## Output layout

Given `output_dir / "overview_name"`, use:

```text
output_dir/
├── overview_name.pdf            # report/publication
├── overview_name.png
└── panels/
    └── overview_name/
        ├── a_descriptive-name.pdf
        ├── a_descriptive-name.png
        ├── b_descriptive-name.pdf
        └── b_descriptive-name.png
```

For `explore`, export PNG only unless the user requests PDF. Follow the selected mode's DPI and vector rules for every standalone panel. Use lowercase panel prefixes in overview order plus short filesystem-safe descriptive names. Never silently overwrite two panels with the same name.

## Re-render; do not crop

Define each panel as a reusable function that accepts an axes and draws only that panel's data and local annotations:

```python
def draw_panel_a(ax, data, *, standalone=False):
    ...
```

Call the same function once for the overview axes and once for a new standalone figure. Re-rendering preserves resolution and lets the standalone version include complete labels, units, legends, colorbars, titles, annotations, and sensible aspect ratios. Do not crop panel pixels from the overview and do not move existing artists between figures.

Panel labels (`a`, `b`, ...) belong to the overview by default; omit them from standalone figures unless they are scientifically meaningful or requested. Allow `standalone=True` to restore labels suppressed in shared-axis layouts and to replace shared legends/colorbars with local ones.

## Standalone colorbars

Whenever numeric magnitude is encoded by color—including heatmaps, contour maps, surfaces, scalar-colored scatter plots, spatial fields, and microscopy intensity maps—give every standalone panel its own colorbar. Never rely on the overview's shared colorbar.

Make the standalone colorbar more prominent than the overview version by allocating more width/height and separation, using the panel's normal readable text size, and showing clear representative ticks plus a concise quantity-and-unit label. As a practical starting point, use a thickness near 4–6% of the panel axes and a visible pad near 2–4%; adapt to the figure rather than treating these as fixed journal rules.

Prominence means easier to find and read, not stronger or different data encoding. Preserve exactly the overview's `Normalize`/`LogNorm`/`BoundaryNorm`, `vmin`, `vmax`, center, boundaries, colormap, direction, units, and tick semantics. Never rescale each standalone panel independently when panels are meant to be compared. Use `fig.colorbar(mappable, ax=ax, ...)` or a dedicated colorbar axes belonging to the standalone figure; never paste or crop the overview colorbar.

Do not create a colorbar for discrete category colors. Use a complete legend with visible category labels instead.

## Standalone completeness

- Make each panel understandable without neighboring panels: restore omitted axis labels, units, tick labels, legends, colorbars, and necessary annotations.
- Treat a missing local colorbar on any numeric color-mapped standalone panel as an incomplete export.
- Preserve the same data, transformation, limits, normalization, palette, and visual encoding as the overview unless a changed limit is explicitly requested.
- Keep shared comparisons comparable. For heatmaps, reuse the overview's normalization even when exporting panels separately.
- Choose a standalone canvas appropriate to that panel; do not inherit the overview grid cell's cramped dimensions.
- Exclude blank spacer axes, decorative axes, shared legend/colorbar axes, and text-only sidebars by default. Export a text panel only when it is a requested deliverable.
- Close each standalone figure after saving to avoid memory buildup when many panels are generated.

## Verification

Visually inspect the overview plus representative standalone panels; inspect all panels for formal delivery when practical. For every numeric color-mapped panel, confirm that its standalone colorbar is present, more readable than the overview colorbar, labeled with quantity and units, and identical in scale and meaning. Confirm the expected file count and run:

```text
scripts/inspect_outputs.py <overview-stem> --mode <mode> --panels-dir <panels/overview_name> --expected-panels <N>
```
