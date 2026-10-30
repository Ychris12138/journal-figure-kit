# Using the skill in different agents

The scientific workflow, scripts, reference paths and color approvals are shared across hosts. Resolve `scripts/` and `references/` relative to this installed skill folder, not the user's current working directory. Write generated figures in the user's project.

| Host | Invoke / verify discovery | Explicit-use control |
|---|---|---|
| Codex | `$journal-matplotlib`; inspect the skills list | `agents/openai.yaml` keeps `allow_implicit_invocation: false` |
| Claude Code | `/journal-matplotlib` | The installer adds `disable-model-invocation: true` |
| Cursor | `/journal-matplotlib` | The installer adds `disable-model-invocation: true` |
| VS Code Copilot | `/journal-matplotlib`; Open Customizations → Skills | The installer adds `disable-model-invocation: true`; this adapter targets VS Code, not every Copilot client |
| Gemini CLI | `/skills list`, `/skills reload`, then explicitly ask to use `journal-matplotlib` | The description and body require an explicit request; the host has its own activation consent |
| OpenCode | Ask to load `journal-matplotlib` with the native `skill` tool | The description/body require an explicit request; optional host permission `skill: {"journal-matplotlib": "ask"}` adds a loading prompt |
| Other agents | Explicitly provide this `SKILL.md` path | Requires file reading, Python execution and image/PDF inspection; no native integration claim |

Gemini/OpenCode do not receive a fabricated frontmatter switch that claims to prevent automatic loading. Their native loading policy and model adherence are separate from these instructions. The installer does not alter global permissions, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, editor rules or user settings. Do not automatically rewrite them to make this skill always active.

For external agents, use the host's own file-reading, shell, browsing and image/PDF inspection tools. No Codex-specific tool name is required. If a host cannot show images or browse journal sources, state the missing capability and provide reviewable files/source limitations instead of claiming visual QA or current compliance.

`local_runtime.json`, when present, records a Python environment created or selected during installation. Treat it as local configuration: verify the executable exists and use it explicitly. Do not copy its absolute path into a public release. `requirements.txt` specifies the plotting dependencies; only the optional installer setup step installs them.

Host interfaces were checked against official docs on 2026-10-30: [Codex](https://developers.openai.com/codex/skills/), [Claude Code](https://code.claude.com/docs/en/skills), [Cursor](https://cursor.com/docs/skills), [Gemini CLI](https://geminicli.com/docs/cli/skills/), [OpenCode](https://opencode.ai/docs/skills/), [VS Code](https://code.visualstudio.com/docs/agent-customization/agent-skills). Directory/metadata installation is tested separately from live model behavior. Do not infer that all host applications have been exercised end to end.
