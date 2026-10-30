# Journal Figure Kit

[English](README.md) | **简体中文**

**让科研图在论文最终尺寸下，依然清楚可读。**

[快速安装](#quick-install) · [效果与验证](docs/validation.md) · [下载 v0.11.0](https://github.com/Ychris12138/journal-figure-kit/releases/tag/v0.11.0)

[![Validate](https://github.com/Ychris12138/journal-figure-kit/actions/workflows/validate.yml/badge.svg)](https://github.com/Ychris12138/journal-figure-kit/actions/workflows/validate.yml)

面向物理、化学和分子模拟、可适配多种 agent 的科研作图 skill 与 Python 工具集：先确认配色和物理含义，再按最终尺寸构图，检查字号、遮挡和实际导出文件，交付可编辑 PDF 与高分辨率 PNG。

项目名是 **Journal Figure Kit**，skill 名称保留 **`journal-matplotlib`**。支持 Codex、Claude Code、Cursor、Gemini CLI、OpenCode 与 VS Code Copilot 的安装适配。

<a id="quick-install"></a>

## 快速安装

### 一键安装（推荐）

需要 **Python 3.12+**。不用手动下载文件，也不需要 Git 或 Node.js。

**Windows PowerShell 5.1+：**

```powershell
irm https://raw.githubusercontent.com/Ychris12138/journal-figure-kit/main/install.ps1 | iex
```

**macOS、Linux、WSL 或 Git Bash：**

```bash
curl -fsSL https://raw.githubusercontent.com/Ychris12138/journal-figure-kit/main/install.sh | bash
```

默认执行：**安装到当前用户的 Codex、配置独立 Python 环境、升级前保存旧版 ZIP 备份**。脚本自动查找 Python、安装作图依赖和适配文件，并复用已有 Codex skill 的安装位置。再次运行即可升级；完成后重新加载 skills 或开启新会话。

命令从 `main` 获取最新入口，入口内部固定对应版本的 Python 安装器。Python 本身需要提前安装；脚本不会修改系统 Python 或 PowerShell 执行策略。

<details>
<summary>选择其他 agent、调整安装范围或检查安装</summary>

例如安装到 Claude Code：

```powershell
& ([scriptblock]::Create((irm 'https://raw.githubusercontent.com/Ychris12138/journal-figure-kit/main/install.ps1'))) --agent claude-code
```

```bash
curl -fsSL https://raw.githubusercontent.com/Ychris12138/journal-figure-kit/main/install.sh | bash -s -- --agent claude-code
```

| 使用的工具 | `--agent` 参数 | 调用方式 |
|---|---|---|
| Codex | `codex` | `$journal-matplotlib` |
| Claude Code | `claude-code` | `/journal-matplotlib` |
| Cursor | `cursor` | `/journal-matplotlib` |
| Gemini CLI | `gemini` | 明确说“使用 journal-matplotlib skill” |
| OpenCode | `opencode` | 明确说“加载 journal-matplotlib skill” |
| VS Code Copilot | `copilot` | `/journal-matplotlib` |

`--agent` 后可填写多个名称。追加 `--scope project` 只给当前项目安装；`--check` 检查文件和依赖；`--dry-run` 预览路径；`--no-deps` 使用已有 Python 环境；`--no-update` 拒绝替换已有安装。检查模式不会安装依赖或更新 skill。

</details>

<details>
<summary>其他安装方式</summary>

已有 Node.js 22.20+、Git 和 Python 作图环境时，也可运行：

```bash
npx skills add Ychris12138/journal-figure-kit
```

它只复制通用 skill，不配置 Python 环境，也不执行本项目的专用适配和备份逻辑。已有源码仓库时，可运行 `python install.py --quick` 完成安装；Codex 用户也可让 `$skill-installer` 安装 `https://github.com/Ychris12138/journal-figure-kit/tree/v0.11.0/skills/journal-matplotlib`。

</details>

[完整安装参数与适配说明](docs/agents.md)。已验证安装与调用元数据；其他 agent 的实际模型会话尚未逐一测试。中文色卡需要 Microsoft YaHei、Noto Sans CJK SC 或 SimHei 等字体。

## 解决哪些问题

![合成多面板科研图示例](docs/assets/overview.png)

*示例使用合成数据；仓库不包含私有科研数据或原论文图片。*

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

在仓库根目录使用安装器输出的 Python 环境；也可先在项目环境运行 `python -m pip install -r requirements.txt`，再执行：

```bash
python -m unittest discover -s tests -v
python examples/gallery.py --output build/gallery
python examples/typography_proof.py --output build/typography
python examples/layout_proof.py --output build/layout
```

每次示例运行使用新的输出目录；导出工具默认拒绝覆盖。测试集包含 **55 项作图测试、26 项安装器测试与 8 项脚本入口测试**，另有五类修复后的合成遮挡案例和 14 对私有真实科研图回归；平台结果和跳过项见验证记录。实际科研图不随仓库发布。模型行为测试提示单独列出，未冒充已经执行的模型基准。

[完整验证记录](docs/validation.md) · [尺寸与导出工具](skills/journal-matplotlib/references/quality-tools.md) · [字号调整](skills/journal-matplotlib/references/typography.md) · [防遮挡用法](skills/journal-matplotlib/references/collisions.md)

## 边界与贡献

自动筛查不能证明完全没有遮挡；细线、低透明度数据、箭头、自定义对象、嵌套布局和三维图需要额外审阅。交付前仍应查看最终尺寸 PNG 和独立渲染 PDF。色觉检查不保证所有人均可辨识，期刊预设也不等于投稿合规认证。

欢迎提交带小型合成复现脚本的 issue，注明 Python/Matplotlib 版本、最终图幅、预期结果与必要的 PNG/PDF；请去除私有数据。修复应保留科学含义，行为问题附带针对性测试。

[更新记录](CHANGELOG.md) · [工具对照](docs/market-comparison.md) · [防遮挡调研](docs/layout-research.md) · [发布说明](docs/release-checklist.md)

## 许可

本项目采用 **[MIT 许可证](LICENSE)**，署名为 © 2026 Ychris12138。第三方依赖与链接论文保留各自的许可和著作权。
