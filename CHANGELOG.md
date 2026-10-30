# Changelog

## 0.11.0 — 2026-10-30

- Add recommended `irm .../install.ps1 | iex` and `curl -fsSL .../install.sh | bash` entrypoints to both language homepages.
- Detect Python 3.12+ and delegate to a pinned Python backend; default to a user-level Codex install with isolated dependencies and backed-up upgrades.
- Add shared `--quick`, `--no-deps` and `--no-update` handling while preserving direct-installer defaults and read-only checks.
- Test native shell pipelines, interpreter detection, argument/path preservation, failures and local install/check behavior; preserve interactive PowerShell sessions on failure.
- Include PowerShell/Bash scripts in release assets and checksums. WSL follows the Linux path but is not separately exercised.

## 0.10.0 — 2026-10-30

- Publish the first normal GitHub Release, with language switching and quick installation at the top of both READMEs.
- Add one-command online installation for Windows, macOS and Linux without manually downloading or saving an installer.
- Support in-memory and stdin entrypoints without relying on `__file__` or an unrelated current-directory skill.
- Retry transient skill-download failures up to three times; preserve existing checksum, backup and explicit-update behavior.
- Add four installer tests; the suite now contains 76 tests. External host model sessions remain outside the executed validation scope.

## 0.10.0-rc.1 — 2026-10-30

- Expand the Chinese README with a prominent entry, agent-specific commands, setup, update and troubleshooting guidance.
- Add a standard-library installer for Codex, Claude Code, Cursor, Gemini CLI, OpenCode, VS Code Copilot and generic file-based use.
- Adapt native invocation metadata while sharing all scientific instructions and plotting tools; document host-enforced versus instruction-only activation controls.
- Support pinned release downloads with SHA256 verification, local/offline sources, optional isolated Python dependencies, previews, receipts, checks and backed-up updates.
- Add installer behavior tests and three-OS CI coverage. Live model sessions in external agent applications remain untested.

## 0.9.0-rc.2 — 2026-10-30

- Adopt the MIT License following the project owner's explicit choice; include it in both the repository and installable skill.
- Update English/Chinese documentation, download links and release archives. Plotting behavior is unchanged from rc.1.

## 0.9.0-rc.1 — 2026-10-30

- Publish as **Journal Figure Kit** with English/Chinese guides and reproducible examples; preserve the installed `journal-matplotlib` name and invocation.
- Add Windows/Linux CI definitions and verify installation plus the 55-test suite in an isolated Windows Python 3.12 environment before publication.

- Add scene-aware layout presets and rendered decoration/data collision screening, including ink hidden by opaque legends.
- Add finite legend/free-note placement, fixed-canvas subplot reflow and explicit reserved legend regions; preserve labels, data, fonts and scientific targets.
- Record intentional heatmap overlays with scoped reasons; retain text collision/clipping checks and disclose unsupported geometry.
- Attach collision audit to paired exports by default; support review, strict and explicitly skipped modes.
- Add synthetic before/after proofs, real-figure regression checks, primary-source skill research and behavior tests.

## 0.8.0-rc.1 — 2026-10-30

- Add eight selectable journal typography profiles with final-placement role sizes, official source locators and explicit limits of verification.
- Add whole-figure font scaling, base-size and absolute role overrides; update existing ticks, legends, colorbars, annotations and tagged panel labels without cumulative scaling.
- Distinguish working-canvas sizes from manuscript placement, warn on journal conflicts without silently changing requested sizes, and audit effective PDF typography after reduction.
- Add reduced-size synthetic proof, behavioral tests and detailed typography guidance. Real research comparison artifacts remain outside the public package.

## 0.7.0-rc.1 — 2026-10-30

- Add exact-size PDF/PNG export with local crop/font settings, pre-export decoration screening, output hashes and failure staging.
- Add grayscale, contrast and optional three-type CVD screening; no automatic palette approval or color substitution.
- Add the six-paper Shi/Tanaka analysis with source-linked physical roles and three pending cards; omit copyrighted source images.
- Add scientific-encoding guidance for decompositions, gaps, independent units and SD/SEM/CI.
- Keep error bars legible on black preview bars using a contrasting halo.
- Measure margins against an explicit uniform background; include PDF UserUnit in physical dimensions.
- Add reproducible synthetic gallery, behavioral regression tests, dependency list, research comparison and release instructions.
- Preserve explicit invocation, three-mode workflow, scoped approvals, journal source caveats, and standalone-panel export requirements.

## 0.6

Reference-image color proposals, versioned palette cards, confirmation checks, paper-derived palette pool and source-aware preview.
