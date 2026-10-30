# Palette selection and evidence

Paper-derived candidates are in [paper-palettes.json](paper-palettes.json); classic named sets remain in [palettes.json](palettes.json). Named Matplotlib maps use the installed library implementation; record its version. Do not alter source colors while still claiming the original palette. No journal in this collection mandates a named palette.

## The pre-plot decision

Ask only for choices not already approved in the current scope. Offer 2–3 relevant versioned cards, with swatches AND the same tiny synthetic example of the intended marks. A swatch alone hides thin-line visibility, alpha blending and dense overlap. Use the card helper described in [palette-cards.md](palette-cards.md). Example prompt:

> 本图有三个体系。A r1 是柔绿/杏橙/灰蓝，B r1 是靛蓝/墨绿/灰紫；每张卡都写明体系与颜色的对应关系，示例数据相同。请选择 A/B。如果都不满意，可以直接发参考图；我会根据图中的颜色另做建议配色卡，等你确认后再用。

When a reference is supplied or candidates are rejected, follow [reference-image-colors.md](reference-image-colors.md). Do not keep cycling the rejected defaults. The reference is inspiration for a new proposal, not approval to recolor the actual figure. Preserve the source samples separately from tuned proposal colors. A revision to colors, roles, mapping, alpha, or numeric normalization invalidates approval for that revised card; an unrelated font or layout correction does not.

For a heatmap, confirm map + meaning + norm + limits instead: e.g. density → cividis, linear 0 to a scientifically justified maximum; free-energy difference → RdBu_r with a stated zero; phase → twilight with explicit periodic range. Reuse mappings across panels and later figures. An approved palette name without the new categories' mapping is not enough to silently swap category identities. Record user delegation if they explicitly ask you to decide.

## Paper-derived starting points

Choose according to the number and meaning of variables. These are approximate raster samples of particular figures, not prescribed journal palettes. Subsetting must retain a documented mapping. Read only the needed library entries.

| Use | Candidate ID | Source figure | Practical limit |
|---|---|---|---|
| Three materials/models | `paper_nature_soft3` | Nature, microplastic–water interfaces, Fig. 3a–b | Soft fills need clear edges |
| Two mechanisms + baseline | `paper_nature_dual3` | Nature, quantum friction, Fig. 2 | Black is a baseline only if explicitly assigned |
| Energy/component decomposition | `paper_ncomms_components5` | Nature Communications, halide interface, Fig. 3 | Add line styles for the two blues |
| Pressure/tension components | `paper_pre_mechanics4` | PRE, cell monolayer mechanics, Fig. 2c | Region shading is separate from data colors |
| Four to five variants | `paper_jcp_variants5` | JCP, condensate wetting, Fig. 2 | Inspect yellow-green at final size |
| Thermodynamic components | `paper_jpcl_components5` | JPCL, Widom line, Fig. 2 | Pale colors may need adjustment for thin lines |
| Mechanism on/off | `paper_pnas_mechanism2` | PNAS, nematic mixture, Fig. 3C–D | Two qualitative groups, not a continuous map |
| Four structure conditions | `paper_science_structure4` | Science, chromatin condensates, Fig. 2I–K | Author-manuscript figure; local panel mapping |

Full source URLs, version and sampling limitations are stored with each entry. The three starter cards use matching three-group synthetic plots to compare the visual families; their `Group 1–3` labels are placeholders for preview, not approval of a real dataset's mapping.

## Classic alternatives

Offer these when the user requests them or the figure's needs justify them; do not automatically re-offer a rejected family.

| Use | Candidate | Alternative | Caveat |
|---|---|---|---|
| Two experimental systems | Okabe–Ito blue / vermillion | Tol high contrast blue / red | Combine color with line/marker; no inferred chemical meaning |
| Three categories | Tol high contrast | Okabe–Ito | Better grayscale distinction still needs output inspection |
| Four to six categories | Okabe–Ito subset | Tol bright | Bright yellow/cyan are weak thin marks on white |
| Seven to nine categories | Tol muted | Facet or direct labels | Do not cycle a short palette or invent near-identical extras |
| Density, rate, population, nonnegative magnitude | cividis | viridis; magma for suitable intensity images | Linear/log norm follows the data, not fashion; show units |
| Signed deviation with meaningful reference | RdBu_r | Optional scientific diverging map such as vik, if already installed | Explicit midpoint; sign remains labeled in grayscale |
| Wrapped phase/angle | twilight | A verified cyclic scientific map | Endpoints must join; do not use for temperature |

Use gray for reference/uncertainty/missing only through an explicit mapping. Missing ≠ zero. A missing-data mask should be distinguishable from a colormap's midpoint and under-range values. Uncertainty bands can use the same category color with a recorded alpha on a white background, after checking that overlap does not masquerade as another category. Do not use palette colors for tiny text; use dark neutral text and swatches/keys.

## Classical and recent evidence (checked 2026-10-28)

1. **Okabe & Ito, Color Universal Design** — [author resource](https://jfly.uni-koeln.de/color/), **Fig.16** supplies the categorical set; **Fig.14** illustrates redundant shapes/lines. The JSON reorders the original colors to postpone low-contrast yellow. Exact hex values come from the published palette, not a paper screenshot. [Wong 2011, Nature Methods](https://doi.org/10.1038/nmeth.1618) is related background; full publisher text was inaccessible during this audit, so it adds no independently verified numeric rules.
2. **Nuñez, Anderton & Renslow 2018, PLOS ONE** — [paper](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0199239), **Figs.4–5**, introduces cividis optimized for ordinary and red–green-deficient vision. Supports cividis as a quantitative sequential option; does not make every cividis figure accessible regardless of labels/normalization.
3. **Kaspar & Crameri 2022, Angewandte Chemie** — [author-hosted paper](https://www.fabiocrameri.ch/ws/media-library/837e86a54d764b30809439421a4fa9da/2022-angewandtechemie-kasparcrameri-coloring-chemistry.pdf), DOI [10.1002/anie.202114910](https://doi.org/10.1002/anie.202114910), **PDF p.2 Fig.1; p.3 Fig.2**. Text and figure captions were read; image rendering was unavailable. The spectroscopy, structure and reaction-screen examples motivate separating supporting color from quantitative color, adding noncolor cues, and using perceptually ordered maps. No exact palette was extracted from these figures.
4. **Schneider et al. 2026, ice nucleation on microcline (001)** — [published article](https://doi.org/10.1038/s41467-026-76548-7), published 25 August 2026. The later 40-paper study inspected the [PMC-archived Fig. 3](https://pmc.ncbi.nlm.nih.gov/articles/PMC13507223/#Fig3), superseding the earlier preprint-only check. It combines colored cycle markers on an AFM background with a gray statistical reference. Design inference: choose the image map and category marks separately; test overlay contrast; encode reference vs experiment redundantly. Do not call the green background a journal preference.
5. **Paul Tol's maintained palette notes** — [source](https://sronpersonalpages.nl/~pault/), **Figs.1,2,4** and “Qualitative colour schemes”, updated 16 August 2026. Exact hex values are available as text. These are current maintained design resources, not a new physics paper. Bright, high-contrast and muted are offered for different group counts; high contrast explicitly considers grayscale.

This is a focused selection of classical methods and a recent, relevant physics example, not a systematic survey of every current journal. Publication in a prestigious journal does not certify a figure's colors. Separate (a) exact reusable published palettes, (b) literature-backed visualization principles, and (c) qualitative inspiration from an observed figure.

## Verification and reproduction

- Inspect actual exported marks on their real background, including transparency, grayscale, and common red/green CVD simulations. Simulations approximate vision; do not promise universal accessibility.
- Treat qualitative distinctions, ordered magnitudes, signed quantities and cyclic variables differently. `TwoSlopeNorm` with unequal endpoint distances has unequal slopes on either side; record that choice. Centering does not justify inventing symmetric data limits.
- Validate missing/under/over colors and colorbar extensions. Never truncate outliers merely to improve contrast without explaining the data decision.
- Use symbols/line styles for categorical spectra, transport curves and phase comparisons; keep them stable between overview and standalone panels. Preserve conventional atom-species colors where needed, but add a key and accessible structure labels rather than silently recoding chemistry.
