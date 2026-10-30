# Agent behavior evaluation cases

These cases are future regression prompts for an explicitly invoked skill. They are not claimed as independently executed model benchmarks. Helper-level automated results are in `validation.md`. Review generated artifacts and conversation decisions, not just whether particular words appear.

| Prompt / setup | Observable success | Failure to catch |
|---|---|---|
| “这些配色不喜欢，照我给的参考图重新做三张卡。” Reference image has colored phase regions and black data. | Inspect actual image; distinguish regions from data; show synthetic cards and approximate sampling provenance; keep actual-data recoloring pending | Treat reference upload as approval; mislabel background regions as CI |
| “使用刚确认的 E 配色，只把图例放外面并去掉多余白边。” Confirmed mapping is present. | Reuse scoped approval; reserve legend space; exact final mm and unchanged data/mapping; show new PNG/PDF | Ask again for unchanged colors; tight-crop into wrong dimensions; shrink text excessively |
| “这个文件有一百万个轨迹帧，给我 95% CI。” Only mean and SD columns exist. | Identify missing independent sampling/interval method; do not invent n or label 1.96 SD as mean CI; proceed with independent layout work | Frame-wise pseudo-replication or silently changed error definition |
| “合并两张热图，再分别导出，每张单图自己有色条。” Norm already fixed. | Shared normalization and units; regenerate standalone panels with readable colorbars and preserved physical aspect | Crop standalone panels out of overview; independently autoscale color ranges |
| “按 Science 最终投稿规范输出。” Official source inaccessible. | State exact source limitation; give provisional output with user-supplied dimensions; do not fabricate page/section or compliance | Pretend an old/blocked source was verified; use another journal's dimensions |
| “改用红色表示另一种状态，别重新展示。” Earlier confirmation binds red to the first state. | Explain mapping changed, create a revised concrete card; request only the unresolved color choice | Apply stale fingerprint; confuse a layout-only change with semantic remapping |
| “图例挡住曲线，保持字号和范围。” Opaque legend hides a segment. | Detect hidden data ink, finite candidate search, reserve space if no solution; preserve all identity entries | Judge only final white legend patch; shrink text; expand axis limits; drop same-text series |
| “整体字号放大 15%，仍按单栏输出。” Enlarged legend is now crowded. | Reapply final-size typography, rerun collision audit, inspect PNG/PDF after targeted repair | Reuse a stale pre-enlargement audit; assume DPI fixes overlap |
| “检查这张热图的标题、色条和格内数字。” Numeric labels intentionally overlay cells. | Scoped reasoned text-data exemption, while checking text-text, clipping and neighboring panels | Blanket exemption for all axes; move cell values into unrelated cells |
| “给这些数据点标名字，不要漏掉。” Dense point-linked labels. | Preserve target positions; bounded text placement and leader-line review; report unsolved cases | Move scientific targets or silently omit labels to force a pass |

For each real run, record model/version, input artifacts, choices actually given by the user, output paths, measured dimensions, missed issues and correction. Promote a demonstrated failure into a small reproducible helper test or a focused instruction; avoid accumulating generic rules without evidence.
