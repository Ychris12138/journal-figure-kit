# Journal Figure Kit

**让科研图在论文最终尺寸下，依然清楚可读。**

[English](README.md) · [下载 v0.9.0-rc.1](https://github.com/Ychris12138/journal-figure-kit/releases/tag/v0.9.0-rc.1) · [效果与验证](docs/validation.md)

[![Validate](https://github.com/Ychris12138/journal-figure-kit/actions/workflows/validate.yml/badge.svg)](https://github.com/Ychris12138/journal-figure-kit/actions/workflows/validate.yml)

面向物理、化学和分子模拟的 Codex 作图 skill 与 Python 工具集：先确认配色和物理含义，再按最终尺寸构图，检查字号、遮挡和实际导出文件，交付可编辑 PDF 与高分辨率 PNG。

项目名是 **Journal Figure Kit**；安装后的调用名保留 **`$journal-matplotlib`**。

![合成多面板科研图示例](docs/assets/overview.png)

*示例使用合成数据；仓库不包含私有科研数据或原论文图片。*

## 解决哪些问题

| 常见问题 | 处理方式 |
|---|---|
| 边框大、外部留白多 | 先设计固定尺寸、面板、图例和色条区域，再测量实际导出边距。 |
| 配色随意，状态颜色不一致 | 展示带版本的配色卡，确认颜色与物理量的映射；布局修改复用已有确认。 |
| 想参考某篇文章的颜色 | 从参考图分离数据色、背景色与标注色，提出近似色卡，确认后应用。 |
| 插入论文后文字太小 | 按最终放置宽度计算字号，支持整体倍率、正文基准及各字段独立覆盖。 |
| 图例、标题或坐标轴挡内容 | 渲染后检查文字和真实数据墨迹，有限次调整位置，无解则预留独立区域。 |
| 总图拆开后不能直接使用 | 重新生成完整独立子图，保留数值、颜色、单位、归一化和色条。 |
| 期刊要求查不到出处 | 记录官方链接、章节/PDF 页码和未确认之处，区分期刊规定与本地预设。 |

美化不改数据、拟合、误差定义或缺失观测；不会靠缩小已确认字号、改变坐标范围或删掉图例条目来消除遮挡。

## 安装

需要 Codex 和 Python 环境；发行测试使用 Python 3.12。skill 只在显式调用时启用。

在 Codex 中可以直接说：

```text
使用 $skill-installer 安装这个 skill：
https://github.com/Ychris12138/journal-figure-kit/tree/v0.9.0-rc.1/skills/journal-matplotlib
```

也可从 [Release](https://github.com/Ychris12138/journal-figure-kit/releases/tag/v0.9.0-rc.1) 下载 skill ZIP，把其中的 `journal-matplotlib` 文件夹放到 `$CODEX_HOME/skills/`；未设置时通常为 `~/.codex/skills/`。已有同名版本时先备份。安装后开启新 Codex 会话。

Python 工具和示例建议使用独立环境：

```bash
git clone https://github.com/Ychris12138/journal-figure-kit.git
cd journal-figure-kit
git checkout v0.9.0-rc.1
python -m venv .venv
```

PowerShell 使用 `.venv\Scripts\Activate.ps1` 激活，bash 使用 `source .venv/bin/activate`，随后运行：

```bash
python -m pip install -r requirements.txt
```

告诉 Codex 在该环境中运行作图脚本。工具不会自行安装依赖或改动持久化 Matplotlib 配置。中文色卡需要 Microsoft YaHei、Noto Sans CJK SC 或 SimHei 等字体；科学图测试采用 DejaVu Sans。

## 直接这样用

```text
$journal-matplotlib 帮我重画这张结构因子图，目标 JCP，最终宽度 85 mm。
保留原数据与拟合，先给配色卡，等我确认再用新颜色。
导出 PDF 和 600 dpi PNG。
```

```text
$journal-matplotlib 保持刚确认的配色，所有字放大 10%，图例固定 9 pt。
按最终排版尺寸重查遮挡。
```

```text
$journal-matplotlib 参考这张图片重新给我配色卡，解释数据、误差和背景各用什么颜色。
```

```text
$journal-matplotlib 图例挡住曲线了。保持字号和数据范围，寻找空白位置，
没有合适位置就预留图例行。总图和完整独立子图都要导出。
```

三种模式：`explore` 用于快速探索，`report` 用于报告 PDF/PNG，`publication` 明确毫米尺寸、最终字号及 600 dpi PNG。期刊名称不能代替具体图宽和投稿阶段要求。

## 看实际差异

![图例遮挡修复前后](docs/assets/layout-legend.png)

*曲线、颜色、字号与坐标范围不变；图例通过检查后移动到空白位置。*

- [五类布局修复对照 PDF](docs/assets/layout-comparison.pdf)：图例遮曲线、密集图、子图标题/轴标签、长刻度、说明文字。
- [最终尺寸字号对照 PDF](docs/assets/typography-proof.pdf)：解释大画布的 8 pt 为何缩小后难以阅读。
- [待确认配色卡 PDF](docs/assets/palette-cards.pdf)：近似论文取色与语义映射示例。

## 期刊和配色来源

覆盖 Nature、Nature Communications、PRL、PRE、JCP、JPCL、PNAS、Science。预设保留官方来源、具体位置和访问/时效限制，不把本地默认值当作期刊强制要求。

工具包内置八组可选论文配色预设，另有 Rui Shi / Hajime Tanaka 六篇论文的图级分析。论文颜色是近似视觉参考，不是作者源码的精确 HEX，也不是某期刊的官方配色。最终按物理含义和图形语义选择。

[期刊来源](skills/journal-matplotlib/references/journals.md) · [字号依据](docs/typography-research.md) · [Shi/Tanaka 分析](skills/journal-matplotlib/references/shi-tanaka.md) · [参考图取色流程](skills/journal-matplotlib/references/reference-image-colors.md)

## 测试与复现

在仓库根目录、已激活环境中运行：

```bash
python -m unittest discover -s tests -v
python examples/gallery.py --output build/gallery
python examples/typography_proof.py --output build/typography
python examples/layout_proof.py --output build/layout
```

每次示例运行使用新的输出目录；导出工具默认拒绝覆盖。当前记录包括 **55 项通过的工具测试**、五类修复后的合成遮挡案例和 14 对私有真实科研图回归。实际科研图不随仓库发布。模型行为测试提示单独列出，未冒充已经执行的模型基准。

[完整验证记录](docs/validation.md) · [尺寸与导出工具](skills/journal-matplotlib/references/quality-tools.md) · [字号调整](skills/journal-matplotlib/references/typography.md) · [防遮挡用法](skills/journal-matplotlib/references/collisions.md)

## 边界与贡献

当前为发布候选版。自动筛查不能证明完全没有遮挡；细线、低透明度数据、箭头、自定义对象、嵌套布局和三维图需要额外审阅。交付前仍应查看最终尺寸 PNG 和独立渲染 PDF。色觉检查不保证所有人均可辨识，期刊预设也不等于投稿合规认证。

欢迎提交带小型合成复现脚本的 issue，注明 Python/Matplotlib 版本、最终图幅、预期结果与必要的 PNG/PDF；请去除私有数据。修复应保留科学含义，行为问题附带针对性测试。

[更新记录](CHANGELOG.md) · [工具对照](docs/market-comparison.md) · [防遮挡调研](docs/layout-research.md) · [发布说明](docs/release-checklist.md)

## 许可

**目前尚未授予开源许可，保留所有权利。** 仓库公开可见，开源许可证仍待所有者选择。见 [LICENSE](LICENSE)。第三方依赖与链接论文保留各自的许可和著作权。
