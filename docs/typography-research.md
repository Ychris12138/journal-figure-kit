# 最终排版字号：来源与实例

检查日期：2026-10-30。以主文科研图为范围；区分期刊要求、样本观察和本 skill 的设计选择。没有对各期刊全部论文做随机抽样，不能声称得到期刊平均字号。

## 官方来源

| 期刊 | 查到的字号要求/建议 | 具体位置与本次可访问性 |
|---|---|---|
| Nature | 最终普通文字 5–7 pt；面板字母 8 pt 加粗正体 | [在线图指南](https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels/)，Figure sizing、Fonts；[官方 artwork PDF](https://www.nature.com/documents/nature-final-artwork.pdf#page=1)，第 1 页 Fonts and labels；均读取 |
| Nature Communications | 预期印刷尺寸下最佳 5–8 pt | [官方 PDF](https://www.nature.com/documents/ncomms-submission-guide.pdf#page=1)，第 1 页 Figures；文件明确为 2019-05-03，不能当成当前完整规则 |
| PRL / PRE | 页面上字形高度和符号宽度至少 2 mm | [APS 2024 Style Guide](https://res.cloudinary.com/apsphysics/image/upload/v1736779890/APS_Journals_Style_Guide_Authors_Nov2024_ua91lv.pdf#page=43)，文件第 43 页、印刷第 42 页，II.S.1 Content；已读取 |
| JCP | 图例/标注至少 8 pt，按 100% 排版尺寸制作 | [AIP Author Instructions](https://publishing.aip.org/resources/researchers/author-instructions/)，Preparing Your Graphics → Guidelines → For all other journals；已读取。网页其他期刊的 10 pt 推荐不能移用给 JCP |
| JPCL | 最终发表图文字至少 4.5 pt | [ACS JPCL guide](https://researcher-resources.acs.org/publish/author_guidelines?coden=jpclcd)，Appendix 2: Preparing Graphics → Size；已读取，页面更新 2026-10-08 |
| PNAS | 先前记录为缩小后 6–12 pt | [Submitting your manuscript](https://www.pnas.org/author-center/submitting-your-manuscript)，Figures；2026-10-28 项目记录已核对，本次 403，保留时效标记 |
| Science | 未获得本次可核实的当前官方点数范围 | [Revised manuscript instructions](https://www.science.org/content/page/instructions-preparing-revised-manuscript)，本次 403；8 pt 为本地草稿建议，不用 Science Advances 代替 |

## 三个版面实例

1. **Yuan、Qiu、Sun、Tanaka，Nature Communications 2026，Fig. 1，出版 PDF 第 2 页**：[Competing hydrogen-bond orders drive water’s anomalous surface tension](https://doi.org/10.1038/s41467-026-69356-6)。图字不可直接作为 PDF 字体提取；在该页最终版面上，将图区以 600 dpi 渲染，隔离刻度数字 `200` 得到约 **2.96 mm 的墨迹高度**；小写面板 a 约 **2.58 mm**。这是字形高度，不是原始字号；不同字体的 em/x-height 不同，不能倒推一个精确 pt。观察支持“字相对于小面板应足够大”，不能据此覆盖期刊规范。该论文作者含 Tanaka，不含 Rui Shi。
2. **Lin 等，Science 2021，Fig. 2，PDF 第 3 页**：[作者托管的出版版 PDF](https://web.stanford.edu/group/ihmegroup/cgi-bin/MatthiasIhme/wp-content/papercite-data/pdf/singh2021hydronium.pdf)。图字同样不可直接提取。选定刻度 2 的墨迹高度约 **1.86 mm**，面板 C 约 **2.71 mm**。与上一例有可见差异；不要把大小写字形高度差直接解释为相同点数差。文章实例不能确证 Science 当前稿件要求。
3. **Vigil 等，2024，Fig. 2，作者预印本第 2 页**：[Measuring Topological Constraint Relaxation in Ring-Linear Polymer Blends](https://arxiv.org/pdf/2404.15560)。指定图区可提取的主要字为 **12 pt**，数学脚标约 **8.4 pt**。它是作者预印本，不是 PRL 最终制作版；用于说明物理图常采用较大图字，不能作为最终期刊字号统计。

字形测量用人工选定区域、灰度阈值 128、隔离字符的主要连通分量，存在抗锯齿/栅格化/边界选择误差；报告约数。论文图未加入发行包，只保留来源和方法。可提取文本为空时不编造字体读数，读不到当前官方指南时不把博客转载升级为规则。

## 实现取舍

我们的默认普通文字集中在 **7–9 pt 的最终尺寸**，Nature 取允许范围上端，NC 取旧指南上端；JCP 留出最小值以上的余量。不同标题的限制分别保存。字体大小相对于整图的比例由最终图宽自然产生，不把字号按整图宽度无限放大。

`final_pt = canvas_pt × placed_width / canvas_width`。180 mm 的图缩到 90 mm，8 pt 变成 4 pt；600 dpi 也不会改变它。新图优先直接用最终尺寸构图；兼容大画布时给字体做逆向补偿，并另审线宽/点大小。

支持“整体 +10%”、指定正文基准、按语义角色分别调整。改字号不改数据和配色；不因字号调整重新索要配色批准。遇到小面板装不下时重排布局，不能偷偷把字体缩回去。超出已记录期刊范围时明确警告，不静默截断用户的设置。

[字体配置及命令](../skills/journal-matplotlib/references/typography.md) · [可执行合成打样示例](../examples/typography_proof.py)
