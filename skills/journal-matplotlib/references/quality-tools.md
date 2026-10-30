# Geometry and palette tools

## Exact canvas export

Import `export_pair` from the installed skill's `scripts/figure_export.py`. For a standalone project copy that helper together with `scripts/layout_audit.py` and `references/layout-presets.json`, preserving their relative structure. Construct the figure at its intended size first:

```python
from figure_export import export_pair
result = export_pair(
    fig, "outputs/figure1", width_mm=89, height_mm=65, dpi=600,
    provenance={"data": "data/profile.csv", "script": "plot_profile.py",
                "uncertainty": "SD across independent runs", "n_independent": 8},
)
```

The example uncertainty metadata is illustrative, not a default for new data. Include the approved card fingerprint and confirmation reference in the scientific `.figure.json` contract. `.export.json` records rendering facts and hashes; it is not a substitute for that contract. The helper validates dimensions without changing figure geometry; scoped `savefig.bbox=None` prevents inherited tight cropping. It keeps PDF text as embedded TrueType where supported and preserves dense raster layers at the requested export DPI. It never creates additional image detail.

Outputs are staged before publication; replacement of each file is atomic but a multi-file set is not a transaction. Prefer unique stems. Existing files require `overwrite=True`; a failed render leaves no newly published pair. Inspect `layout_warnings` and then run `inspect_outputs.py` against both files. The bounding-box screen is heuristic and cannot prove that annotations do not overlap.

Since 0.9, the manifest also includes a rendered `collision_audit` (default `collision_mode='warn'`). It detects risks from text/legend boxes, axis frames, neighboring panels and isolated data ink. Use `'error'` to require a clear screen with no skipped scope before writing files; `'off'` explicitly records the skipped check. See [collisions.md](collisions.md) for repair and reasoned heatmap overlays. `inspect_outputs.py` still checks file properties and margins; it cannot recreate live plot semantics from a flattened image.

## Palette screening

```text
python scripts/palette_audit.py --deck references/shi-tanaka-cards.json --output palette-review
```

Writes PDF/PNG with original, grayscale and available deutan/protan/tritan simulations, plus JSON measurements. Requires Matplotlib; Colorspacious enables CVD simulation. Missing Colorspacious is an explicit skipped check (exit 1), not a pass. `--no-cvd` deliberately requests grayscale-only screening and is also recorded as skipped. Exit 0 means requested computations completed; it does **not** mean the palette is universally accessible or approved.

- Contrast uses sRGB relative luminance; band contrast uses the proposed alpha composited on the declared background. WCAG-style contrast values do not become universal print or thin-line thresholds.
- Grayscale preserves relative luminance. Pairwise CIE L* differences below 5 are review hints, not a standard or a pass/fail criterion.
- CVD uses Colorspacious's documented Machado et al. 2009 simulation at severity 100. Out-of-gamut values are clipped for display and counted. This is a screening model; examine the actual plotted lines, markers, overlaps, legend and text at final size.
- Continuous cards are screened at their supplied anchors only. No claim is made about full-path monotonicity, uniformity, interpolation or diverging-center behavior. Review the rendered colormap with the confirmed normalization.
- The tool never changes a card or records confirmation. Any proposed adjustment still needs a revised card and the user's approval.

Method: [Colorspacious tutorial](https://colorspacious.readthedocs.io/en/latest/tutorial.html), [Matplotlib savefig](https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.savefig.html). Consulted 2026-10-30.

## Nonwhite margins and PDF units

The inspector's `--background '#F2F2F2'` identifies the uniform canvas background used to measure edge padding. Transparency is composited on that background and disclosed. The retained `--white-threshold` option measures RGB distance from the selected background for backward compatibility. A textured background or a full-bleed image requires visual judgment; neither white-pixel percentage nor a zero margin is a quality score.

PDF physical dimensions include `/UserUnit`. A rotated page or different CropBox is flagged for manual review rather than treated as an ordinary unrotated figure. Font resources, metadata and geometric checks complement visual inspection; they do not establish journal acceptance.
