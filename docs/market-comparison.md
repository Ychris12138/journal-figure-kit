# 科研作图工具对照与取舍

调研日期：2026-10-30。阅读了下列 4 个公开 skill 的入口与相关说明，以及 2 个成熟 Matplotlib 样式库的文档。本表是功能与方法对照，不是安装量排行榜，也没有对这些外部项目进行同任务运行排名。公开 skill 的版本会变化。

| 项目与阅读位置 | 值得学习 | 本项目的具体落地 | 没有照搬的部分 |
|---|---|---|---|
| [K-Dense Scientific Visualization](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/scientific-visualization/SKILL.md) | 科学含义优先；分清出版要求与默认值；明确缺失数据、独立样本与导出审计的局限 | 补充物理问题到图形的选择表、相关采样与误差定义；实际配色筛查；精确画布导出 | 不增加 Plotly、Seaborn、交互网页等本 skill 暂未验证的支持范围；不声称检查通过即期刊合规 |
| [sci-paper-plot-skill](https://github.com/FFFxueGawaine/sci-paper-plot-skill/blob/main/SKILL.md) | 项目默认值复用；作图目的优先；编辑前看代码和图；提供可运行模板 | 复用既有约定；项目输出与 skill 分离；共享绘图函数生成总图与独立子图；合成 gallery | MSSP 特定的字体、标题、命名限制不推广到 Nature、APS 等杂志；不增加普通绘图的反复审批 |
| [Icarus-Figures](https://github.com/TAO-QKV/Icarus-Figures/blob/main/.claude/skills/icarus-figures/SKILL.md) | 先明确科学主张；图形类型目录；渲染后检查；源码与图保持可复现关系 | 图形语义指南、机器检查加人工视觉验收、导出 hash 与生成参数 | 不承诺编辑无修改接收；不强制每幅图提供 CI；不为了完整而一律输出 SVG 或引入 TikZ |
| [SciDER Scientific Visualization](https://github.com/leonardodalinky/SciDER/blob/main/.scider/skills/scientific-visualization/SKILL.md) | 强调误差定义、可读性、多面板组织和图注 | 加强 SD/SEM/CI 区分；先保留数据含义再改布局 | 阅读版本的误差带示例用 `y_std * 1.96` 标成 CI，不能一般化为均值 CI；通用 tight 裁边、全局 rcParams 和统一最小字号不适合精确期刊版面 |
| [SciencePlots](https://github.com/garrettj403/SciencePlots)（样式库） | 可组合样式、临时样式上下文、成熟的线条和字体基础设置 | 所有修改局限于 rc_context；检验不污染调用方全局样式 | 样式名不能证明当前期刊合规；不默认引入 LaTeX 或额外字体环境 |
| [tueplots](https://github.com/pnkraemer/tueplots)（样式库） | 图幅匹配论文文本宽度、字号一致、返回独立配置字典 | 显式毫米尺寸；不自动缩放最终成图；PNG/PDF 独立实测 | 不把某个会议模板尺寸套到其他期刊；不把样式库当作配色确认系统 |

K-Dense 和上述库已经覆盖了不少基本原则，因此“有配色表”“会设置 DPI”不足以形成差异。这个 skill 更明确的重点是：

1. **先给可审阅的色卡，再记录真实确认**：参考图可替代候选；颜色、类别身份、排序、alpha、数值归一化变动会使旧确认失效。
2. **按物理身份保持颜色一致**：从 Shi/Tanaka 的具体图学习数据、分量、总量、区域底色和温度序列的分工，而不是用作者名或期刊名固定一套颜色。
3. **对精确尺寸负责**：同时检查 PNG 实际物理尺寸、PDF 页面、嵌入字体和图像；分别处理外边距、面板间距、物理数据空区。
4. **完整导出独立子图**：复用绘制函数，保持相同归一化，每幅数值色彩图有自己的色条。
5. **把失效模式变成回归测试**：覆盖全局 tight 裁边、过期配色确认、PDF 单位、非白底边距、导出失败等；相关采样与误差表述另列真实会话评估案例。科学判断仍需人工审阅。

本轮仅吸收方法与设计经验，未复制上述项目的源文件或论文原图进入发行包。新增 helper 与测试在本项目内实现；保留来源链接便于追溯。色觉与导出 API 另核对了 [Colorspacious 官方教程](https://colorspacious.readthedocs.io/en/latest/tutorial.html) 和 [Matplotlib savefig 文档](https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.savefig.html)。
