# Layout recipes

For executable collision screening, finite repair helpers and scene presets, read [collisions.md](collisions.md). Run it after final typography; repeat after fonts, ticks, labels, legends or canvas change. Layout engines alone do not prove that legends or annotations avoid data.

## Diagnose whitespace before changing the canvas

Measure blank **outer edges around all visible content**, not all white pixels. Sparse line plots legitimately have large white interiors. The inspector's defaults flag an outer edge only when it exceeds both 4 mm and 5% of that dimension; these are adjustable local review heuristics, not journal limits. Even a good score can hide a bad internal layout or an isolated stray artist.

1. Outer canvas padding: call `fig.canvas.draw()`; inspect text/legend/colorbar extents. Remove unused GridSpec rows/columns and oversized figure margins. Keep a small physical breathing space (start around 1–2 mm outside visible labels).
2. Interpanel gaps: budget axes, tick labels, panel tags and colorbars separately. Use shared alignment and only share tick labels where scientifically unambiguous. Long labels can wrap or move to a dedicated key.
3. Inside axes: preserve physically meaningful ranges, common comparison scales and image aspect. Do not narrow limits, crop microscopic features or remove baselines to satisfy a white-area metric.
4. Fixed-aspect images: choose figure/GridSpec geometry matching the image's aspect plus colorbar space. Do not stretch the image; a long skinny colorbar or an overly wide reserved cell can cause false-looking borders.

For exact-size exports, set `figsize=(W/25.4,H/25.4)` and `savefig.bbox=None` inside the local rc context; export without tight cropping and compare PNG physical size and PDF MediaBox. `bbox_inches='tight'` changes the exported dimensions; changing its padding does not fix this contract. If tight export is deliberately requested, measure and disclose the resulting size, or rebuild the figure at the required final size and recheck text sizes.

Check `Axes.get_tightbbox(renderer)` for rendered axes decorations and `Text.get_window_extent(renderer)` for figure/axes annotations outside `fig.bbox` before saving, including artists excluded from the layout. Do not blindly scan all tick Text objects: locators may retain ticks outside the view interval that are never rendered. Off-canvas annotation detection is a visual/bbox check; the exported bitmap alone cannot recover content already clipped. Intentional clipping of data at axes boundaries is different. Do not falsely treat hidden or clipped data-line extents as a text-layout error.

The file inspector can flag likely excess padding or contact with the canvas border; it never crops automatically. Fix the source layout and export again. Keep the approved palette and source data unchanged during this repair.

## Construction recipes

Choose the smallest relevant recipe. Design the layout before plotting; do not rely on a final `tight_layout()` call to repair structural crowding.

| Risky scene | Preferred construction | Avoid |
|---|---|---|
| Simple single axes | `layout="constrained"`; modest margins | Excess empty decoration |
| Multi-panel | `GridSpec`/subfigures; reusable panel draw functions; export overview plus standalone panels | Cropping panels from the overview |
| Long text sidebar | Dedicated axes with `axis("off")` and an explicit width ratio | Large off-canvas `fig.text()` blocks |
| Outside/shared legend | Reserve a legend column, row, or figure-level region | Covering dense data or shrinking every panel |
| Heatmap/colorbar | Compact shared colorbar in the overview; a more prominent local colorbar in every standalone numeric color-mapped panel; identical normalization | Missing standalone colorbar or independently rescaled panels |
| Long category labels | Increase width, wrap labels, or rotate no more than needed | Shrinking below readable size |
| Top annotations/significance | Reserve vertical headroom and set limits deliberately | Letting annotations sit outside the canvas |
| Dense scatter/mesh | Use alpha and suitable marks; rasterize only the dense artist if needed | Dropping or smoothing data for appearance |
| Image/microscopy panel | Preserve aspect; add labeled colorbar/scale bar as vector objects | Stretching images or baking labels into pixels |
| Insets/twin axes | Set positions and margins explicitly; merge legend entries | Combining layout engines blindly |
| Exact journal size | Build at final inches and inspect at final display size | `bbox_inches="tight"` changing page dimensions |

## Collision-resistant rules

- Call `fig.canvas.draw()` before measuring or repositioning artists.
- Reserve space rather than repeatedly reducing font size.
- Place panel labels in axes coordinates so they stay consistent.
- Keep shared layout code separate from panel drawing so each data panel can be re-rendered independently.
- Keep legends inside only when they do not obscure data; otherwise allocate a separate region.
- Use a common normalization and one shared colorbar for comparable heatmaps.
- Reuse that exact normalization for each standalone panel, but give each one its own clearer and more prominent colorbar.
- For shared axes, remove redundant labels without removing essential units.
- Use `subplots_adjust` only for layouts that `constrained_layout` cannot handle; do not combine incompatible layout methods casually.

## Visual QA loop

1. Render once at the intended canvas and final font sizes.
2. Inspect every edge, tick label, legend, colorbar, annotation, and panel label.
3. Inspect the PNG at 100% and at intended final size.
4. For publication, confirm PDF dimensions, embedded font resources, and that the complete page is not one raster image.
5. Fix the layout and repeat; never report success from code inspection alone.
