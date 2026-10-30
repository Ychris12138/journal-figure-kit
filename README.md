# Journal Figure Kit

**Scientific figures that remain readable at manuscript size.**

[简体中文](README.zh-CN.md) · [Download v0.9.0-rc.2](https://github.com/Ychris12138/journal-figure-kit/releases/tag/v0.9.0-rc.2) · [Examples and validation](docs/validation.md)

[![Validate](https://github.com/Ychris12138/journal-figure-kit/actions/workflows/validate.yml/badge.svg)](https://github.com/Ychris12138/journal-figure-kit/actions/workflows/validate.yml)

A Codex skill and Python toolkit for publication figures in Matplotlib. Confirm colors and their meaning, compose at the final physical size, check typography and collisions, and export an editable PDF with a high-resolution PNG.

Built for physics, chemistry and molecular simulation workflows. The installed skill keeps the invocation name **`$journal-matplotlib`**.

![Synthetic multi-panel scientific figure with an outside legend](docs/assets/overview.png)

*Synthetic example. The repository contains no private research data or copied paper figures.*

## What it helps with

| Figure problem | Approach |
|---|---|
| Large borders or wasted outer space | Construct a fixed-size canvas, allocate panels, legends and colorbars explicitly, and measure exported margins. |
| Arbitrary or inconsistent colors | Show versioned color cards, confirm the mapping to physical quantities, and reuse that approval for layout-only changes. |
| A reference figure has the colors you want | Separate data colors from backgrounds and annotations, propose approximate color cards, then confirm before recoloring. |
| Text becomes tiny in the manuscript | Plan font sizes at the intended placement width; support overall scaling and role-specific overrides. |
| Legends, labels or titles cover content | Measure rendered decorations and isolated data ink; try bounded repairs or reserve a separate region. |
| Multi-panel figures need standalone exports | Regenerate complete panels with consistent data, colors, units and normalization. |
| Journal guidance is hard to trace | Keep official links, section/page locators and verification limits beside the presets. |

The workflow preserves source data, uncertainty definitions, missing observations and scientific identities. It does not change axis limits or shrink approved text simply to clear an overlap warning.

## Install

Requires Codex and a Python environment. Python 3.12 is the release test target. The skill activates only when explicitly invoked.

**With Codex's skill installer**, ask:

```text
Use $skill-installer to install the skill from
https://github.com/Ychris12138/journal-figure-kit/tree/v0.9.0-rc.2/skills/journal-matplotlib
```

**Manual installation:** download the skill ZIP from the [release page](https://github.com/Ychris12138/journal-figure-kit/releases/tag/v0.9.0-rc.2), then put its `journal-matplotlib` folder in `$CODEX_HOME/skills/`, or `~/.codex/skills/` when `CODEX_HOME` is unset. Back up an existing installation before replacing it. Start a new Codex session after installing.

For the Python tools and runnable examples, clone the repository and install dependencies in a dedicated environment:

```bash
git clone https://github.com/Ychris12138/journal-figure-kit.git
cd journal-figure-kit
git checkout v0.9.0-rc.2
python -m venv .venv
```

Activate with `.venv\Scripts\Activate.ps1` in PowerShell or `source .venv/bin/activate` in bash, then run:

```bash
python -m pip install -r requirements.txt
```

Tell Codex to use this environment for your figure project. Helpers do not install packages or change persistent Matplotlib settings. Chinese palette previews need a CJK font such as Microsoft YaHei, Noto Sans CJK SC or SimHei; scientific test figures use DejaVu Sans.

## Use it

Start with your data or plotting script, target journal and intended final width. Existing project choices and confirmed color mappings are reused.

```text
$journal-matplotlib Redraw this structure-factor plot for JCP.
Use an 85 mm final width, preserve the fit and data, propose color cards,
and wait for my choice before applying new colors. Export PDF and 600 dpi PNG.
```

```text
$journal-matplotlib Keep the approved colors. Increase all text by 10%,
set the legend to 9 pt at final size, and check again for overlaps.
```

```text
$journal-matplotlib Use this reference image to propose a new color card.
Explain which colors represent data, uncertainty and background.
```

```text
$journal-matplotlib The legend covers the curve. Keep the fonts and axis
limits; find a clear position or reserve a legend row. Export each panel too.
```

Three modes scale the work: **explore** for quick PNGs, **report** for PDF/PNG pairs, and **publication** for explicit millimeter dimensions, final-size typography and 600 dpi PNGs. A journal name alone does not determine the correct width or submission-stage requirements.

## See the difference

![Before and after: an opaque legend is moved away from a hidden curve](docs/assets/layout-legend.png)

*The curve, colors, fonts and axis limits are unchanged. The legend moves only after a rendered collision check.*

- [Five layout comparisons — PDF](docs/assets/layout-comparison.pdf): legends, dense plots, panel labels, long ticks and notes.
- [Final-size typography comparison — PDF](docs/assets/typography-proof.pdf): why an 8 pt label on a large canvas can become too small after placement.
- [Color-card examples — PDF](docs/assets/palette-cards.pdf): proposed mappings awaiting confirmation.

## Journal and color references

Presets cover **Nature, Nature Communications, PRL, PRE, JCP, JPCL, PNAS and Science**. Each title has source locators and explicit limits of verification. Older or inaccessible guidance is marked; local defaults are distinguished from publisher requirements.

The toolkit includes eight optional paper-derived palette presets and a separate six-paper Rui Shi / Hajime Tanaka analysis. Paper-derived colors are approximate visual references, not exact author source colors or journal-mandated palettes. Choose by the figure's physical meaning, not by journal branding.

[Journal sources](skills/journal-matplotlib/references/journals.md) · [Typography evidence](docs/typography-research.md) · [Shi/Tanaka analysis](skills/journal-matplotlib/references/shi-tanaka.md) · [Reference-image workflow](skills/journal-matplotlib/references/reference-image-colors.md)

## Reproduce the checks

Run from the repository root in the activated environment:

```bash
python -m unittest discover -s tests -v
python examples/gallery.py --output build/gallery
python examples/typography_proof.py --output build/typography
python examples/layout_proof.py --output build/layout
```

Use a new output directory for each proof run. Export helpers refuse implicit overwrites. The [validation record](docs/validation.md) documents **55 passing helper tests**, five repaired synthetic collision cases, and 14 private real-figure regression pairs. Private artifacts are excluded from this repository. Model-level behavior prompts are listed separately and are not presented as executed benchmarks.

Use the Python helpers directly: [exact-size export and output QA](skills/journal-matplotlib/references/quality-tools.md), [typography controls](skills/journal-matplotlib/references/typography.md), and [collision checks and repairs](skills/journal-matplotlib/references/collisions.md).

## Scope and limitations

This is a **release candidate**. Geometry screening is conservative, not a guarantee of zero collisions. Thin or transparent ink, arrows, custom artists, nested layouts and three-dimensional plots need additional review. Always inspect the exported PNG and an independently rendered PDF at final size. Palette checks do not prove universal accessibility; journal presets do not certify submission compliance.

The skill is designed for Codex. Other agents may be able to read its Markdown instructions, but their behavior has not been validated. See [validation](docs/validation.md) for the exact tested environment and remaining checks.

## Contribute

Open an issue with a small synthetic reproducer, Python/Matplotlib versions, final figure dimensions and the expected result. Include a PNG or PDF when useful; remove private data. Improvements should preserve scientific meaning and include a focused test when they fix a behavioral bug.

[Changelog](CHANGELOG.md) · [Design comparisons](docs/market-comparison.md) · [Collision research](docs/layout-research.md) · [Release notes](docs/release-checklist.md)

## License

Released under the **[MIT License](LICENSE)**. Copyright © 2026 Ychris12138. Third-party libraries and linked papers retain their respective licenses and copyrights.
