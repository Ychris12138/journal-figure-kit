# Choose the encoding from the physical question

Use this guide when the scientific representation is still open. Do not redesign a requested figure merely to exhibit a more elaborate plot type.

| Question | Useful starting point | Meaning to preserve |
|---|---|---|
| How does a profile vary with distance, time or temperature? | Lines with sparse markers; independent trajectories in small multiples if needed | Units, ordering, gaps, physical zero, common comparison limits |
| How do two states or models differ? | Overlaid curves with different markers/line styles, or a directly defined difference panel | State identity across all panels; residual sign and reference model |
| What contributes to a total? | Total plus named component curves | Signed contributions and algebraic relationship; no stacking if it misrepresents cancellation |
| How broad or heterogeneous is a distribution? | ECDF, histogram with explicit edges, or raw points with a summary | Sample size and weighting; KDE bandwidth is an analytical choice |
| How does a scalar field vary? | Heatmap/image with labeled colorbar | Pixel aspect, units, fixed normalization, masked/under/over values |
| Is there a signed deviation from a reference? | Diverging map with physically meaningful center | Center need not be the arithmetic midpoint; disclose asymmetric range |
| Is the variable periodic? | Cyclic map with joined endpoints | Period and units; no artificial boundary at the wrap |

## Uncertainty contract

Record `estimator`, `interval_type`, `interval_method`, `independent_unit`, `n_independent`, and, when relevant, `n_frames`, correlation treatment and random seed. Use `unknown` if the provided data cannot establish a field; ask only for the missing scientific decision that affects the plot.

- SD describes dispersion. SEM estimates uncertainty of a mean under assumptions. A 95% CI requires an actual interval method. Multiplying an SD column by 1.96 does not generally produce a mean CI.
- MD frames, particles, pair distances and overlapping windows are usually dependent. A row count is not an independent replicate count. Reuse the validated analysis; do not introduce a row-wise bootstrap or divide by sqrt(number of frames) merely to draw a narrower band.
- Block averaging/bootstrap may be appropriate only when its assumptions and block scale have been scientifically established. Ask for or report that method; this plotting skill does not infer a trustworthy correlation time from a picture.
- When only a mean and SD are supplied, draw and label SD if requested. Do not relabel it CI, invent n, significance stars or replicate data.
- Separate physical variability, between-run variation, fit uncertainty and measurement uncertainty in captions and marks.

## Gaps, scales and identities

Keep missing observations distinct from zero and excluded values. Retain NaN gaps in Matplotlib lines, or explicitly segment observations; dropping missing rows and connecting the neighbors implies continuity. Log scales require an explicit policy for nonpositive values. Preserve all input data and record any approved transformation.

Use a shared mapping keyed by physical identity, not loop position. A blue state must stay blue in its profiles, schematic annotations, legends and standalone exports. If a different figure encodes a different variable (temperature rather than state), name the new mapping and confirm it. Store numerical normalization once and pass it to every comparable panel.

For black bars with black uncertainty, retain the data color and use a narrow background-colored halo behind the error bars. Review at final size; the halo is a drawing aid, not an additional uncertainty interval.
