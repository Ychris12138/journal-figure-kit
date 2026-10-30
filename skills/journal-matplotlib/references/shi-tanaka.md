# Shi–Tanaka: colors follow physical roles

Source review: 2026-10-28. This release packages the prior figure-level analysis; it does not claim a new full-text review. HEX values are approximate image samples, not author-supplied values. Original figures are linked, not redistributed.

| Paper / figure | Observed roles | Reusable lesson | Caution |
|---|---|---|---|
| [PNAS 2018: Origin of the emergent fragile-to-strong transition in supercooled water](https://doi.org/10.1073/pnas.1807821115) — Fig. 3A–B；参照 Fig. 2 | 黑圆、红方、蓝三角区分三种动力学量；图中区域另用浅绿、浅粉和窄亮绿带标出。 | 数据颜色和区域底色分工明确；圆、方、三角与线型提供第二层辨识。β 的蓝色轴标签与蓝色数据一致。 | 双纵轴表达不同物理量，必须保留轴标与单位；不因配色相同就合并量纲。 |
| [Science Advances 2019: Distinct signature of local tetrahedral ordering in the scattering function of covalent liquids and glasses](https://doi.org/10.1126/sciadv.aav3194) — Fig. 2；参照 Fig. 4A–D | 红实线、蓝虚线和黑点划线分别对应三个部分结构因子；对应特征峰的箭头与公式也用红、蓝。 | 这是最直接的物理角色配色：数据、峰位箭头、公式和示意图互相呼应，三色已经足够。 | 同一篇 Fig. 4C 的绿色表示分峰面积，含义与 Fig. 2 不同；必须逐图核对颜色用途。 |
| [PNAS 2020: The anomalies and criticality of liquid water](https://doi.org/10.1073/pnas.2008426117) — Fig. 3B–D；参照 Fig. 2 与 Fig. 4 | Fig. 3B–D 用蓝到浅色再到红表示温度递增，符号形状区分实验来源；温度值直接写在曲线附近。 | 颜色承担有序变量，符号承担来源，避免把每条曲线当作无序类别。 | Fig. 2 的蓝／红对应高／低压力；不能把跨图的红蓝统一误读为温度。四个 HEX 只是近似取样点，不是完整色标。 |
| [Nature Communications 2023: Impact of hierarchical water dipole orderings on the dynamics of aqueous salt solutions](https://doi.org/10.1038/s41467-023-40278-x) — Fig. 2c、f；参照 Fig. 1 与 Fig. 3 | Fig. 2c 用橙色五边形和紫色六边形区分 B 的正负；Fig. 2f 则用黑、红、蓝区分离子族。 | 离散机制分类与连续场采用不同编码；边界还用圈、方、三角，线与符号能跨热图保持可见。 | 热图色标方向依物理量而异。勘误补充了 Fig. 3 的灰色球说明，分析采用修正版本。 |
| [Nature Communications 2026: Competing hydrogen-bond orders drive water’s anomalous surface tension](https://doi.org/10.1038/s41467-026-69356-6) — Fig. 2a–d；与 Fig. 1a 比较 | Fig. 2 采用总量黑色、S-state 蓝色、ρ-state 橙色，圆／方／三角随曲线在各面板重复。 | 很适合界面 profile 与总量分解：黑色保留给总量，两个分量用清晰的冷暖色。 | 这里分析的是不同图之间的可视化一致性，不是对科学结论的质疑。不得照抄跨图换色。 |
| [Nature Reviews Physics 2019: Revealing key structural features hidden in liquids and glasses](https://doi.org/10.1038/s42254-019-0053-3) — Fig. 3a–b | 暗灰三角、红圆、蓝方、橙三角区分结构描述符；绿色曲线单独承担两态模型预测。ζ 在 a 中连线为黑色。 | 比纯红纯蓝更克制，仍保持清晰的色相差异；颜色、点型和模型曲线的角色分工都明确。 | 浅灰渐变底是原图视觉设计，不代表概率或误差；新图建议先用白底。红色线与圆点像素略有差别，HEX 只作近似代表。 |

## Three pending cards

- D: red / blue / black, inspired by the three partial structure factors in Science Advances 2019 Fig. 2.
- E: blue / orange / black, inspired by components and total in Nature Communications 2026 Fig. 2. Black may represent total only after that semantic mapping is confirmed.
- F: red / blue / gray, a three-category subset from Nature Reviews Physics 2019 Fig. 3.

`shi-tanaka-cards.json` uses placeholder groups and remains pending. Map real variables, preview, audit and confirm before plotting real data. The 2026 paper has Tanaka as a coauthor; Rui Shi is acknowledged, not a coauthor. The 2019 review analysis used the public figure and abstract; full text was subscription-restricted.

Do not assume an author uses one universal palette: in the 2026 paper Fig. 1 and Fig. 2 the same state can have different colors. Our workflow uses one explicit identity-to-color mapping across a figure family. Background phase regions are not automatically uncertainty bands. Temperature, pressure and categorical state require separate declared encodings.

Machine-readable evidence, sampling method, original figure URLs and hashes: [shi-tanaka-evidence.json](shi-tanaka-evidence.json).
