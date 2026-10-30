# 防遮挡方案调研与取舍

日期：2026-10-30。通过公开网络搜索发现相关项目，重点阅读了以下 5 个公开 skill 的原始入口/参考文件，并核对 Matplotlib 与标签布局库官方资料。这不是全网穷尽列表，也不是对外部 skill 的同任务性能排名。外部文件作为研究材料，不执行其安装脚本或附加指令；未复制第三方源码进入本项目。

| 项目 / 实际阅读位置 | 可借鉴方法 | 本项目取舍 |
|---|---|---|
| [K-Dense Scientific Visualization](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/scientific-visualization/SKILL.md)，Implement with scoped styles、Inspect delivered files | constrained layout；固定物理尺寸；导出后审阅 | 沿用一个布局引擎，增加具体冲突对象与可运行修复工具 |
| [SSCI-Plots multi-panel](https://github.com/O0000-code/SSCI-Plots/blob/main/references/multi-panel.md)，§7 shared legend、§13.3 | 给共享图例预留区域、嵌套 GridSpec | 采用独立图例格；不按文字自动去重；不靠 tight 裁边保持画布 |
| [Bioresearcher QA gates](https://github.com/yeyuan98/bioresearcher-skills/blob/main/skills/bioresearcher-plot-making/references/qa-gates-and-gotchas.md)，Three-Layer QA、Vector PDF Collision Audit | 几何筛查与视觉检查并用；区分有意覆盖 | 实现面向 Matplotlib 的对象边界框和真实数据墨迹筛查；没有照搬 PDF 流解析器或统一 5 pt 门槛 |
| [SNAD charts](https://github.com/snadaiapp-png/SNAD/blob/main/skills/charts/SKILL.md)，anti-overlap / legend placement | 渲染后测量、图外图例、有限次修改 | 不采用无条件向画布外推图例、固定大边距或所有重叠都禁止的规则；该仓库入口标 proprietary，未复制代码 |
| [TikZ diagrams skill](https://github.com/RongqinChen/tikz-diagrams-skill/blob/main/SKILL.md)，Collision-repair loop | 按冲突类型修复；重新渲染；只处理剩余问题 | 转为二维科研图检查表与最多三轮修复；没有引入 TikZ 依赖 |

## 库与 API 核对

- [Matplotlib constrained layout](https://matplotlib.org/stable/users/explain/axes/constrainedlayout_guide.html)：能分配标题、坐标轴等装饰空间，支持 GridSpec/色条；混用 tight layout 与手动布局有局限。审计临时冻结布局，以免隐藏文字时布局改变。
- [Matplotlib legend guide](https://matplotlib.org/stable/users/explain/axes/legend_guide.html)：当前版本支持 figure legend 的 outside 位置；普通外置锚点与保留空间是两回事。本项目主要使用显式保留区域。
- [Matplotlib Legend API](https://matplotlib.org/stable/api/legend_api.html) 与 [Text API](https://matplotlib.org/stable/api/text_api.html)：使用渲染器测量文字与图例边界，按候选位置重绘。`loc='best'` 不是零遮挡保证。
- [adjustText](https://adjusttext.readthedocs.io/en/latest/)：在所有坐标范围、图幅确定后调整，一次处理一个 axes，保留指向原数据的箭头；本轮未安装/执行此额外库，不作为默认自动修复承诺。
- [textalloc](https://github.com/ckjellson/textalloc)：提供候选位置、避开点/线等约束；无可行位置时有强制绘制或不绘制标签的选项。科研图不能静默漏掉必需标签，所以本轮使用保留原对象并报告未解决问题的有限搜索。

## 本轮实际实现

1. 先按最终字号和画布构图，按稀疏线图、密集图、热图、多面板、长标签选择预设。
2. 测量装饰边界，同时临时隔离数据层渲染。这样能检查白底图例下面隐藏的曲线，也不会把一条曲线的整个矩形范围都误当成数据。
3. 对图例做有限候选搜索，对普通子图间距重排，对自由说明文字有限避让。没有位置则恢复原位，提示重建独立区域。
4. 特定热图数值可以声明“有意覆盖数据”，带理由入审计；其他碰撞检查继续执行。
5. 每次配对导出附带检查记录。警告模式保留可审阅草图；严格模式拒绝未解决问题。PNG 和独立渲染 PDF 仍须检查。

没有为了降低冲突数而改变点、分箱、拟合、误差定义、颜色、坐标范围或字体。最终效果与实测结果见 [验证记录](validation.md)，可运行案例见 [layout_proof.py](../examples/layout_proof.py)。
