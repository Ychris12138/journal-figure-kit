# Journal Figure Kit

**English** | [简体中文](README.zh-CN.md)

**Scientific figures that remain readable at manuscript size.**

[Quick install](#quick-install) · [Examples and validation](docs/validation.md) · [Download v0.11.0](https://github.com/Ychris12138/journal-figure-kit/releases/tag/v0.11.0)

[![Validate](https://github.com/Ychris12138/journal-figure-kit/actions/workflows/validate.yml/badge.svg)](https://github.com/Ychris12138/journal-figure-kit/actions/workflows/validate.yml)

An agent skill and Python toolkit for publication figures in Matplotlib. Confirm colors and their meaning, compose at the final physical size, check typography and collisions, and export an editable PDF with a high-resolution PNG.

Built for physics, chemistry and molecular simulation workflows, with installation adapters for Codex, Claude Code, Cursor, Gemini CLI, OpenCode and VS Code Copilot. The skill name remains **`journal-matplotlib`**.

## Quick install

### One-click installation (recommended)

Requires **Python 3.12+**. No manual file downloads, Git or Node.js are needed.

**Windows PowerShell 5.1+:**

```powershell
irm https://raw.githubusercontent.com/Ychris12138/journal-figure-kit/main/install.ps1 | iex
```

**macOS, Linux, WSL or Git Bash:**

```bash
curl -fsSL https://raw.githubusercontent.com/Ychris12138/journal-figure-kit/main/install.sh | bash
```

The default is **Codex, current-user installation, a separate Python environment and a ZIP backup before upgrades**. The script detects Python, installs plotting dependencies and the host adapter, and reuses the existing Codex skill location when present. Run it again to upgrade. Reload skills or start a new agent session afterwards.

The commands fetch the latest bootstrap from `main`; each bootstrap pins a matching release of the Python installer. Installing Python itself is a prerequisite. Nothing changes your system Python or shell policy.

<details>
<summary>Choose another agent, change scope or check an installation</summary>

For Claude Code, use:

```powershell
& ([scriptblock]::Create((irm 'https://raw.githubusercontent.com/Ychris12138/journal-figure-kit/main/install.ps1'))) --agent claude-code
```

```bash
curl -fsSL https://raw.githubusercontent.com/Ychris12138/journal-figure-kit/main/install.sh | bash -s -- --agent claude-code
```

| Agent | `--agent` | Invoke |
|---|---|---|
| Codex | `codex` | `$journal-matplotlib` |
| Claude Code | `claude-code` | `/journal-matplotlib` |
| Cursor | `cursor` | `/journal-matplotlib` |
| Gemini CLI | `gemini` | Ask explicitly to use `journal-matplotlib` |
| OpenCode | `opencode` | Ask explicitly to load `journal-matplotlib` |
| VS Code Copilot | `copilot` | `/journal-matplotlib` |

Use several names after `--agent` to install multiple adapters. Add `--scope project` for the current project, `--check` to check existing files/dependencies, `--dry-run` to preview paths, `--no-deps` to use your existing Python environment, or `--no-update` to refuse replacement. Checks do not install dependencies or update the skill.

</details>

<details>
<summary>Other installation methods</summary>

If you already have Node.js 22.20+, Git and a Python plotting environment:

```bash
npx skills add Ychris12138/journal-figure-kit
```

This copies the generic skill without configuring Python or running this project's host-specific adapters and backup logic. From a cloned repository, `python install.py --quick` runs the full setup locally. Codex users can also ask `$skill-installer` to install `https://github.com/Ychris12138/journal-figure-kit/tree/v0.11.0/skills/journal-matplotlib`.

</details>

[Full installation and compatibility guide](docs/agents.md). Installation and metadata are tested; live model sessions in every host have not been benchmarked. Chinese palette previews need a CJK font such as Microsoft YaHei, Noto Sans CJK SC or SimHei.

## What it helps with

![Synthetic multi-panel scientific figure with an outside legend](docs/assets/overview.png)

*Synthetic example. The repository contains no private research data or copied paper figures.*

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

Use a new output directory for each proof run. Export helpers refuse implicit overwrites. The suite contains **55 plotting tests, 26 installer tests and 8 shell-bootstrap tests**; the [validation record](docs/validation.md) reports platform results and skips, five repaired synthetic collision cases, and 14 private real-figure regression pairs. Private artifacts are excluded from this repository. Model-level behavior prompts are listed separately and are not presented as executed benchmarks.

Use the Python helpers directly: [exact-size export and output QA](skills/journal-matplotlib/references/quality-tools.md), [typography controls](skills/journal-matplotlib/references/typography.md), and [collision checks and repairs](skills/journal-matplotlib/references/collisions.md).

## Scope and limitations

Geometry screening is conservative, not a guarantee of zero collisions. Thin or transparent ink, arrows, custom artists, nested layouts and three-dimensional plots need additional review. Always inspect the exported PNG and an independently rendered PDF at final size. Palette checks do not prove universal accessibility; journal presets do not certify submission compliance.

Cross-agent installation and metadata are tested; live model behavior in every host has not been validated. See [validation](docs/validation.md) for the exact tested environment and remaining checks.

## Contribute

Open an issue with a small synthetic reproducer, Python/Matplotlib versions, final figure dimensions and the expected result. Include a PNG or PDF when useful; remove private data. Improvements should preserve scientific meaning and include a focused test when they fix a behavioral bug.

[Changelog](CHANGELOG.md) · [Design comparisons](docs/market-comparison.md) · [Collision research](docs/layout-research.md) · [Release notes](docs/release-checklist.md)

## License

Released under the **[MIT License](LICENSE)**. Copyright © 2026 Ychris12138. Third-party libraries and linked papers retain their respective licenses and copyrights.
