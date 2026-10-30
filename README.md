# Journal Figure Kit

**Scientific figures that remain readable at manuscript size.**

**[中文说明与快速安装](README.zh-CN.md)** · [Download v0.10.0-rc.1](https://github.com/Ychris12138/journal-figure-kit/releases/tag/v0.10.0-rc.1) · [Examples and validation](docs/validation.md)

[![Validate](https://github.com/Ychris12138/journal-figure-kit/actions/workflows/validate.yml/badge.svg)](https://github.com/Ychris12138/journal-figure-kit/actions/workflows/validate.yml)

An agent skill and Python toolkit for publication figures in Matplotlib. Confirm colors and their meaning, compose at the final physical size, check typography and collisions, and export an editable PDF with a high-resolution PNG.

Built for physics, chemistry and molecular simulation workflows, with installation adapters for Codex, Claude Code, Cursor, Gemini CLI, OpenCode and VS Code Copilot. The skill name remains **`journal-matplotlib`**.

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

## Quick install

Download **[install.py](https://github.com/Ychris12138/journal-figure-kit/releases/download/v0.10.0-rc.1/install.py)**, then run with Python 3.12:

```bash
python install.py --agent codex --scope user --with-deps
```

Change `codex` to your agent from the table below. The standalone installer downloads the pinned release, verifies its checksum, installs the host-specific files and creates a separate Python environment. Git, Node.js, administrator rights and manual environment activation are not required. Omit `--with-deps` if your project already has the plotting dependencies.

| Agent | `--agent` | How to invoke |
|---|---|---|
| Codex | `codex` | `$journal-matplotlib` |
| Claude Code | `claude-code` | `/journal-matplotlib` |
| Cursor | `cursor` | `/journal-matplotlib` |
| Gemini CLI | `gemini` | Explicitly ask to use `journal-matplotlib` |
| OpenCode | `opencode` | Explicitly ask to load `journal-matplotlib` |
| VS Code Copilot | `copilot` | `/journal-matplotlib` |
| Other agents with file/shell access | `generic` | Provide the installed `SKILL.md` path |

```bash
# Install several agents, sharing one Python environment
python install.py --agent codex claude-code cursor --scope user --with-deps

# Project-local installation (the default scope)
python install.py --agent gemini --scope project

# Preview / update with backup / check the installation
python install.py --agent codex --scope user --dry-run
python install.py --agent codex --scope user --update
python install.py --agent codex --scope user --check
```

Existing installs are not replaced without `--update`. Updates save a ZIP backup and preserve a recorded Python environment. Use `--venv PATH` with `--with-deps` to choose an environment location, or `--dest PATH` for a custom skills directory. Reload skills or start a new agent session afterwards.

**Compatibility means installation and metadata support.** Live model sessions in every host have not been benchmarked. Codex, Claude Code, Cursor and VS Code receive native explicit-use controls; Gemini/OpenCode retain an explicit-request instruction and their own activation policy. See the [agent guide](docs/agents.md) for directories, official sources and exact limitations.

### Install from source or with Codex

Clone the repository or extract the source ZIP, then run the same `python install.py ...` command from its root; it uses the bundled skill without downloading it. Codex's existing installer also works:

```text
Use $skill-installer to install
https://github.com/Ychris12138/journal-figure-kit/tree/v0.10.0-rc.1/skills/journal-matplotlib
```

That route copies the canonical skill and does not set up Python dependencies. Run the bundled `requirements.txt` in your chosen environment, or use this project's installer with `--update --with-deps`. For manual installation, copy the complete skill folder to the [host's native directory](docs/agents.md), not only `SKILL.md`.

Chinese palette previews need a CJK font such as Microsoft YaHei, Noto Sans CJK SC or SimHei. Scientific test figures use DejaVu Sans.

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

From the repository root, use the Python environment printed by the installer, or activate a project environment with `python -m pip install -r requirements.txt`:

```bash
python -m unittest discover -s tests -v
python examples/gallery.py --output build/gallery
python examples/typography_proof.py --output build/typography
python examples/layout_proof.py --output build/layout
```

Use a new output directory for each proof run. Export helpers refuse implicit overwrites. The suite contains **55 plotting tests and 17 installer tests**; the [validation record](docs/validation.md) reports platform results and skips, five repaired synthetic collision cases, and 14 private real-figure regression pairs. Private artifacts are excluded from this repository. Model-level behavior prompts are listed separately and are not presented as executed benchmarks.

Use the Python helpers directly: [exact-size export and output QA](skills/journal-matplotlib/references/quality-tools.md), [typography controls](skills/journal-matplotlib/references/typography.md), and [collision checks and repairs](skills/journal-matplotlib/references/collisions.md).

## Scope and limitations

This is a **release candidate**. Geometry screening is conservative, not a guarantee of zero collisions. Thin or transparent ink, arrows, custom artists, nested layouts and three-dimensional plots need additional review. Always inspect the exported PNG and an independently rendered PDF at final size. Palette checks do not prove universal accessibility; journal presets do not certify submission compliance.

Cross-agent installation and metadata are tested; live model behavior in every host has not been validated. See [validation](docs/validation.md) for the exact tested environment and remaining checks.

## Contribute

Open an issue with a small synthetic reproducer, Python/Matplotlib versions, final figure dimensions and the expected result. Include a PNG or PDF when useful; remove private data. Improvements should preserve scientific meaning and include a focused test when they fix a behavioral bug.

[Changelog](CHANGELOG.md) · [Design comparisons](docs/market-comparison.md) · [Collision research](docs/layout-research.md) · [Release notes](docs/release-checklist.md)

## License

Released under the **[MIT License](LICENSE)**. Copyright © 2026 Ychris12138. Third-party libraries and linked papers retain their respective licenses and copyrights.
