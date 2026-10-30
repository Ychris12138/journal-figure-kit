# Color card helper

`scripts/palette_cards.py` renders proposals and records confirmation. Only `preview` needs Matplotlib/NumPy; confirmation/export use the Python standard library. It does not sample images automatically: the agent first inspects the reference and records proposed values and their provenance.

```text
python scripts/palette_cards.py preview --deck cards.json --output preview
python scripts/palette_cards.py confirm --deck cards.json --id B --reply "用 B，应用于这组扩散图" --scope "diffusion figure and standalone panels" --output palette-approval.json
python scripts/palette_cards.py export --deck cards.json --approval palette-approval.json --output plot-palette.json
```

The confirmation command's sample reply is an illustration, never actual approval. Run it only after an equivalent real user instruction. A `--font` path is optional for preview; select an installed CJK font when labels need it. Preview outputs `palette-cards.png`, an editable `palette-cards.pdf`, and `palette-proposal.json` with status `pending`. These are synthetic demonstrations. `export` rejects pending records, changed cards and mismatched fingerprints. It checks the current deck as well as the recorded card so stale colors cannot be silently exported as a newly approved revision. Use a new output directory for revised proposals to preserve prior versions.

## Deck schema

See [palette-card-starter.json](palette-card-starter.json) for complete categorical examples. Each deck contains `schema_version: 1`, a title and `cards` with unique IDs. Each card has:

- `id`, positive integer `revision`, `title`, and `kind` (`categorical`, `sequential`, `diverging`, `cyclic`).
- Categorical: `mapping` is an ordered object of meaningful group labels to full six-digit HEX strings. No repeated colors or silent color cycling. Real group labels are required before confirmation for actual data.
- Continuous: `colors` is a list of HEX anchors, and `normalization` contains `scale` (`linear` or `log`), numeric `vmin`, `vmax`, optional `center`, `units`, and `missing_color`. Diverging scales require an interior center and linear scale. Cyclic endpoints must match, with linear periodic range. Sampled anchors define a proposed interpolated map, not an exact reconstruction.
- `background`, `text`, `reference` are explicit HEX roles; `band_alpha` is 0–1.
- `source` describes a paper or reference image. For images use `{ "type": "reference_image", "path": "...", "region": "panel b curves", "method": "pixel_sampled_approximate" }`; a visible conversation attachment ID can replace a path. An optional `observed_colors` list preserves the sampled/estimated reference colors separately.
- `changes`, `use`, `caveat` explain adjustments, suitable plots and unresolved limitations. Do not describe an accessibility check as passed unless actually performed.

For unknown scientific limits, prepare a visual proposal separately and leave approval pending; do not enter arbitrary data limits merely to satisfy validation. The starter deck is a visual family comparison and uses generic group labels; map the real dataset before asking for its final approval.

## Applying exported settings

Read `plot-palette.json` in the generated plotting script. Use `mapping` for categorical colors, or build a `LinearSegmentedColormap` from `colors` and use the recorded `normalization`. Apply `band_alpha` to the same group's uncertainty fill; do not use it to change the scientific uncertainty. Keep a dark neutral text color, and preserve separate missing-data and reference meanings. Use `mpl.rc_context` and a central configuration; do not change persistent Matplotlib defaults.

The exported object includes ID/revision/fingerprint, source and approval evidence. Copy those references into the existing figure contract. Numerical data/processing and layout choices stay outside the color card. A color or mapping adjustment changes the fingerprint and requires a new approval; changing only the plotting script's typography does not.
