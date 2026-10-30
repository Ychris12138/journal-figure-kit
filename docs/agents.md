# Agent compatibility and installation

Checked against official documentation on **2026-10-30**. The installer adapts directories and invocation metadata; all adapters share the same scientific workflow and Python tools.

| `--agent` | Host | Project skill root | User skill root | Invocation |
|---|---|---|---|---|
| `codex` | Codex | `.agents/skills` | `~/.agents/skills` by default; see legacy handling below | `$journal-matplotlib` |
| `claude-code` | Claude Code | `.claude/skills` | `~/.claude/skills` | `/journal-matplotlib` |
| `cursor` | Cursor | `.cursor/skills` | `~/.cursor/skills` | `/journal-matplotlib` |
| `gemini` | Gemini CLI | `.gemini/skills` | `~/.gemini/skills` | Ask explicitly to use `journal-matplotlib` |
| `opencode` | OpenCode | `.opencode/skills` | `~/.config/opencode/skills` | Ask explicitly to load the skill |
| `copilot` | VS Code Copilot | `.github/skills` | `~/.copilot/skills` | `/journal-matplotlib` |
| `generic` | Other agents with file/shell access | `.agents/skills` | `~/.agents/skills` | Provide the full `SKILL.md` path |

The folder `journal-matplotlib` is created under the selected root. For Codex user installs, an explicit `CODEX_HOME` takes priority. If an existing `~/.codex/skills/journal-matplotlib` is found, the installer updates that location with `--update` instead of creating a duplicate. Use `--dest <skills-root>` for a nonstandard host configuration; the installer does not edit global agent settings.

## Quick installation

Download [install.py](https://github.com/Ychris12138/journal-figure-kit/releases/download/v0.10.0-rc.1/install.py), then use Python 3.12:

```bash
python install.py --agent claude-code --scope user --with-deps
```

The standalone script downloads the pinned `v0.10.0-rc.1` skill ZIP from this repository, verifies its SHA256 against the release checksum file, selects the host directory and creates a separate Python environment. These checks verify transfer integrity; the release and installer remain code you choose to trust. The script does not require Git, Node.js, administrator rights or an activated environment.

From a cloned repository or extracted source ZIP, the same command uses the adjacent `skills/journal-matplotlib` directory and can install without network if `--with-deps` is omitted and your Python environment already has the dependencies.

```bash
# One host; default scope is the current project
python install.py --agent cursor

# Multiple hosts; no dependency installation unless requested
python install.py --agent codex claude-code gemini --scope user

# Explicit project and Python environment
python install.py --agent opencode --project /path/to/project --with-deps --venv /path/to/figure-env

# Preview target paths, without downloading or writing
python install.py --agent copilot --scope user --dry-run

# Update: back up the complete prior skill except Python caches
python install.py --agent claude-code --scope user --update

# Verify installed files and Python dependencies
python install.py --agent claude-code --scope user --check
```

`--with-deps` installs into a virtual environment, never into system Python. The default environment is `~/.cache/journal-figure-kit/venvs/<version>-py<major.minor>`. A custom `--venv` must be absent or already be a valid venv. Installing several hosts in one command shares that Python environment. Without `--with-deps`, use your existing project environment when running the agent; `--check` uses the recorded interpreter or the interpreter running the check.

`--update` creates a timestamped ZIP under `<skills-root>/.journal-figure-kit-backups/`, then replaces only this skill. Local modifications are retained in that backup, not merged into the new files. An existing `local_runtime.json` is preserved when no new environment is requested. A failed directory switch restores the original; multiple host installations are separate operations, not a cross-host transaction. An installation receipt records file hashes and local runtime details. Do not publish those local receipts.

## Invocation and model behavior

Codex retains its existing `agents/openai.yaml` explicit-only policy. Claude Code, Cursor and VS Code Copilot receive `disable-model-invocation: true` in their generated `SKILL.md`. Their adapter copies omit the Codex-only UI metadata. The installer does not rewrite `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, editor rules or agent permission files.

Gemini CLI and OpenCode have different activation systems. Their instructions require an explicit user request, but this is **not** a host-enforced manual-only switch. Gemini has native activation consent; OpenCode can use `permission.skill` with an `ask` value if you configure it. Those settings are not modified by this installer.

After installation, reload skills or start a new session. Gemini provides `/skills list` and `/skills reload`; for VS Code use Open Customizations → Skills. In other hosts, check the skill picker or invoke the skill by name. Avoid installing the same name in overlapping native/shared directories, where precedence may select an older copy.

The adapters have filesystem, metadata, rollback and Python smoke tests. Live Claude Code, Cursor, Gemini, OpenCode and Copilot model sessions have **not** been run in this project. File compatibility is not a model-quality benchmark. A generic chat-only agent without local execution or visual inspection cannot complete the full export/QA workflow.

## Primary sources

- [Codex skills](https://developers.openai.com/codex/skills/): project/user discovery and `agents/openai.yaml` policy. Legacy `$CODEX_HOME/skills` handling also follows the bundled Codex skill-installer used by this project.
- [Claude Code skills](https://code.claude.com/docs/en/skills): native skill folders, slash invocation and `disable-model-invocation`.
- [Cursor skills](https://cursor.com/docs/skills): project/user discovery and manual slash-command behavior.
- [Gemini CLI skills](https://geminicli.com/docs/cli/skills/): discovery tiers, consent, listing and reloading.
- [OpenCode skills](https://opencode.ai/docs/skills/): native directories, ignored unknown frontmatter and permission-based loading.
- [VS Code skills](https://code.visualstudio.com/docs/agent-customization/agent-skills): Copilot-compatible folders, slash invocation and frontmatter. The `copilot` adapter is scoped to VS Code; other Copilot clients may differ.

This release does not claim marketplace registration, native cloud deployment, or integration with every client that can read Agent Skills.
