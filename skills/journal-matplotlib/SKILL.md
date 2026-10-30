---
name: journal-matplotlib
description: Apply a three-mode Matplotlib workflow for exploratory, report, or publication-quality scientific figures. Use only when the user explicitly invokes or names journal-matplotlib; never trigger it automatically for ordinary plotting.
license: MIT
---

# Journal Figure Kit

The installed skill retains the name `journal-matplotlib`. Invoke it with `$journal-matplotlib` in Codex, `/journal-matplotlib` in Claude Code, Cursor or VS Code Copilot, or explicitly request the named skill in Gemini CLI/OpenCode. See [agent usage](references/agent-usage.md) for host-specific controls and limits.

Version 0.10.0. Apply only after explicit invocation. Keep plotting code self-contained and settings inside `mpl.rc_context`; do not install packages or change persistent Matplotlib settings without authorization. Put user scripts, data, defaults and generated output in the figure project, never in this installed skill.

If `local_runtime.json` exists beside this file, use its `python` executable for bundled scripts after checking the path exists. Otherwise use the user's selected project environment. Missing dependencies are setup work, not a reason to change the system Python silently. The installer can create a separate environment when explicitly run with `--with-deps`.

## Establish the figure contract

Reuse choices already given in the conversation/project. Infer and state the mode when unspecified; default to `explore` for ambiguous everyday work.

| Mode | Size | Default deliverables |
|---|---|---|
| explore | Unrestricted | PNG, 180 dpi |
| report | Fit the report | PDF + PNG, 300 dpi |
| publication | Explicit final width and height in mm | Editable PDF + PNG, 600 dpi; additional journal format when needed |

Before publication plotting, establish journal **title, submission stage, figure role** (main / supplementary / TOC), final dimensions, and the scientific meaning of each visual encoding. Read only that journal's entry in [journals.md](references/journals.md). Return its official link and precise section/PDF page to the user. Distinguish publisher requirements, recommendations, and this skill's defaults. Recheck the relevant official source at submission time; an inaccessible/old source cannot support a claim of current compliance. A journal name alone is not a size specification.

Identify the question the figure answers before selecting its geometry. For distributions, trajectories, decompositions, missing observations or uncertainty, read [scientific-encoding.md](references/scientific-encoding.md). Reuse project choices; when editing an existing figure inspect both its code and rendered output before changing it.

## Confirm colors before drawing data

Read [palettes.md](references/palettes.md). Reuse an explicitly approved palette **and semantic mapping** within its approved scope; do not repeatedly ask. Otherwise show 2–3 **versioned color cards**, with swatches, category-to-color mapping or colormap + normalization, and the same small **synthetic** example of the intended marks. Request confirmation before rendering actual data in the new colors. Data preparation and layout work can continue while the choice is pending; silence is not approval.

If the user dislikes the options, invite a reference image in the conversation (or use one already supplied). Follow [reference-image-colors.md](references/reference-image-colors.md): inspect the image, separate data colors from background/uncertainty/annotations, propose a faithful option and an optional readability-adjusted option, show the differences on new cards, and obtain confirmation. Uploading a reference, rejecting old cards, or asking for a revision does not approve unseen new colors. If the user explicitly delegates the final choice, record that instruction as the authorization; never infer delegation.

Use `scripts/palette_cards.py preview --deck <cards.json> --output <directory>`; `references/palette-card-starter.json` demonstrates the new paper-derived choices. The helper records a pending proposal and exports approved plotting settings only after a matching confirmation. Read [palette-cards.md](references/palette-cards.md) for commands and the schema. Use `references/paper-palettes.json` as an optional source pool, selected by figure semantics rather than journal name. Classic palettes remain available in `references/palettes.json` when requested or suitable. Never label approximate samples or adjusted colors as exact source colors or journal requirements.

For liquid structure, scattering or interface profiles, [shi-tanaka.md](references/shi-tanaka.md) explains six paper examples and their different physical roles; `references/shi-tanaka-cards.json` contains three **pending** candidates. Never infer a universal state-to-color mapping from an author or journal. Run `scripts/palette_audit.py --deck <cards.json> --output <directory>` for contrast measurements, grayscale and available CVD simulations; review warnings before confirmation. See [quality-tools.md](references/quality-tools.md) for scope and limitations.

## Build at the final size

Read [profiles.md](references/profiles.md) for runnable plotting. Read [layouts.md](references/layouts.md) for exact sizing, multipanels, outside legends, colorbars, long labels, images, or insets.

For publication or font-size changes, read [typography.md](references/typography.md). Set the intended **manuscript placement width**, distinct from any larger working canvas; choose the journal's local role-based font preset and preserve explicit user overrides. `scripts/typography.py` provides overall `font_scale`, base `body_pt`, and final-point role overrides, including ticks, legends, colorbars, annotations and tagged panel labels. Reflow layout after enlarging text. Audit effective placed sizes with `scripts/audit_placement.py`; higher DPI does not rescue text reduced too far. Record both canvas/final dimensions and font settings; unresolved source limits remain explicit.

- Treat outer canvas padding, interpanel gaps, and empty regions **inside data axes** separately. Fix geometry before shrinking fonts. Never optimize total white-pixel percentage.
- Preserve exact output dimensions; do not use `bbox_inches="tight"` as a universal fix. Repair GridSpec/aspect/legend allocation, then re-export and measure all four outside margins.
- For the PDF/PNG pair, `scripts/figure_export.py::export_pair` preserves the existing final canvas even under a global tight-crop style, screens decorations, and writes hashes plus export provenance. It refuses implicit overwrite and does not resize the figure or approve colors. See [quality-tools.md](references/quality-tools.md).
- For every multi-panel overview, also regenerate every data-bearing panel as a complete standalone figure under an overview subfolder. Follow [panels.md](references/panels.md). Keep each numeric color mapping's colormap, units, normalization, limits, and meaningful ticks identical; each standalone needs its own readable colorbar. Categories use a legend.
- Use one shared configuration for font sizes, line widths, palette mapping, axis limits and normalization, including standalone panels. Journal-specific panel labels override the default.

## Preserve scientific meaning

Never change data, smoothing, filtering, binning, clipping, or error-bar definitions for appearance without scientific justification and user authorization. Do not change a physical image's aspect ratio. Report log/symlog scales, normalization, masked/under/over-range values, error-bar meaning and independent sample counts. Distinguish trajectories/frames from independent simulations. Keep physical zeros, common comparison limits and meaningful whitespace. No rainbow/jet by default; use redundant markers/line styles when color carries categories.

Keep text and axes editable in PDF. Rasterize only dense data layers or image data when needed; changing DPI metadata cannot recover missing image detail. EPS cannot preserve alpha transparency: use an appropriate supported format or explicitly rebuild equivalent opaque artwork and inspect it.

## Verify and deliver

After final typography/layout, read [collisions.md](references/collisions.md) and screen decoration-to-decoration and decoration-to-data obstruction with `scripts/layout_audit.py`. Paired export now records this audit by default. Reflow ordinary subplot spacing, test finite legend/free-note positions, and reserve explicit legend/colorbar cells when needed. Preserve scientific targets, data, limits, colors and font sizes. Declare intentional heatmap text overlays individually with a reason; all other checks remain active. Review skipped scope and unresolved findings rather than treating zero detected boxes as a universal guarantee. Rerun after edits and for every standalone panel; stop after three targeted repair rounds and change composition if necessary.

For report/publication, inspect both exported PNG and a **rendered PDF**, with a final-size view and a zoomed detail view. Verify clipping, glyphs (minus/Greek/subscripts), legend correspondence, overlap, panel order, colorbar units, image aspect and perceived uncertainty. Check grayscale and common color-vision-deficiency simulations for color-dependent interpretation when supported; disclose skipped checks.

Run:

```text
python scripts/inspect_outputs.py <stem> --mode publication --width-mm W --height-mm H --json <qa.json>
```

Optional: `--min-font-pt N --max-font-pt N --dpi N --panels-dir DIR --expected-panels N --background '#FFFFFF'`. PDF font-size limits apply to all visible text, so account for larger panel labels. Overview dimensions are NOT inherited by standalone panels; check each standalone's intended size separately. Exit 0 = automated checks pass, 1 = review warnings, 2 = missing/invalid files or a failed size requirement. Missing dependencies yield explicit skipped-check warnings, never a fabricated pass. See `--help` for margin thresholds (local heuristics, not journal rules).

Automated checks do not prove absence of overlap or cropping, and PDF font resources alone do not prove editability. Fix problems and inspect the changed export. Keep a compact `<stem>.figure.json` with journal/stage/role, source URL+locator+check date, dimensions, approved color-card ID+revision+fingerprint and confirmation evidence, semantic mapping, normalization, source-data/script paths, software versions and unresolved QA warnings. Apply the confirmed mapping consistently to lines, markers, bands, legends, colorbars, overview and standalone panels. Color/mapping/normalization changes require a revised card; layout-only changes keep the existing color approval. Deliver the figure files, source script, contract and brief QA status. Do not claim journal compliance if a requirement remains unverified.
