# Release notes and verification

Project: **Journal Figure Kit**. Current candidate: `v0.10.0-rc.1` (cross-agent installation). First public candidate: `v0.9.0-rc.1`.
Repository: <https://github.com/Ychris12138/journal-figure-kit>.
The installed skill folder and explicit invocation remain `journal-matplotlib`.

## Included

- English and Chinese README files, installation instructions and synthetic examples.
- Versioned palette cards, reference-image proposals and explicit color/mapping approval.
- Eight journal profiles with source locators and limits of verification.
- Final-placement typography controls and reduction auditing.
- Exact-size PDF/PNG export, output provenance, margin and font checks.
- Rendered collision screening, bounded legend/note repair and reserved-region recipes.
- Complete standalone panels with preserved scientific encodings.
- Source and skill ZIPs with SHA256 checksums; no private figures, source data or local paths.
- Standalone `install.py`, host-specific directory/metadata adaptation and optional isolated Python setup.
- Installation previews/checks, explicit updates with ZIP backups, and a shared runtime for multiple selected agents.

## Verification before the first upload

- 55 helper tests passed in the original local environment.
- A separate Windows Python 3.12 venv successfully installed `requirements.txt`; all 55 tests passed with the previous `PYTHONPATH` removed.
- The independent environment exported five synthetic before/after collision cases and the intentional heatmap control.
- Skill metadata validation passed; local Markdown links and public-file scans were checked.
- PNGs and independently rendered PDFs were inspected during figure development. Details are in [validation.md](validation.md).

GitHub Actions runs the helper suite, synthetic layout proof, packaging and six-adapter installation checks on Windows, Ubuntu and macOS. Consult the [Actions page](https://github.com/Ychris12138/journal-figure-kit/actions) for live results; a workflow definition alone is not evidence of a pass. Host model behavior is a separate, unexecuted validation scope.

## Release assets

From a reviewed checkout, run:

```bash
python tools/package_release.py --output build/dist
```

This produces `journal-figure-kit-0.10.0-rc.1-source.zip`, `journal-figure-kit-0.10.0-rc.1-skill.zip`, `install.py`, `SHA256SUMS.txt`, a per-file manifest and package metadata. Checksums cover both ZIPs and the installer. The installable ZIP contains a `journal-matplotlib/` folder, its dependency list and the MIT license. `build/`, Git metadata, virtual environments and Python caches are excluded.

The public release is a prerelease, not a claim of journal certification. Keep unverified journal sources and unsupported collision geometry explicit. Review the source tree and both archives before uploading; do not include private regression artifacts.

## License status

The owner selected the **MIT License** on 2026-10-30. Both the repository and installable skill include the full [license](../LICENSE), with copyright attributed to Ychris12138. Third-party libraries and linked papers retain their own terms. The MIT update is published as `v0.9.0-rc.2`; the earlier `v0.9.0-rc.1` tag and original archives remain available as historical artifacts.
