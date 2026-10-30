"""Export a fixed-size PDF/PNG pair without inheriting global tight-crop settings.

Use inside a figure project; no data processing, resizing, or palette selection.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import platform
import tempfile


def layout_warnings(fig):
    """Screen decorations, not hidden ticks or intentionally clipped data artists."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    canvas = fig.bbox.padded(1)
    items = [(f"axes[{i}]", ax.get_tightbbox(renderer))
             for i, ax in enumerate(fig.axes) if ax.get_visible()]
    items += [(f"figure_text[{i}]", artist.get_window_extent(renderer))
              for i, artist in enumerate(fig.texts + fig.legends)
              if artist.get_visible()]
    return [f"{name}: decoration extends beyond canvas; inspect clipping"
            for name, box in items if box is not None and
            (box.x0 < canvas.x0 or box.y0 < canvas.y0 or
             box.x1 > canvas.x1 or box.y1 > canvas.y1)]


def export_pair(fig, stem, *, width_mm, height_mm, dpi=600,
                provenance=None, overwrite=False, collision_mode='warn'):
    """Return an export manifest. The figure must already have its final size.

    Individual files are replaced atomically after all rendering succeeds; the
    three-file publication is not a transaction. Use a unique stem for each run.
    The caller supplies scientific provenance and obtains color approval.
    """
    import matplotlib as mpl

    for name, value in (("width_mm", width_mm), ("height_mm", height_mm), ("dpi", dpi)):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise ValueError(f"{name} must be finite and positive")
    actual = [float(v) * 25.4 for v in fig.get_size_inches()]
    if any(abs(a-b) > 1e-5 for a, b in zip(actual, (width_mm, height_mm))):
        raise ValueError("Figure size differs from contract; rebuild its layout at final dimensions")
    if provenance is not None and not isinstance(provenance, dict):
        raise ValueError("provenance must be a dictionary")
    if collision_mode not in ('warn','error','off'):
        raise ValueError("collision_mode must be warn, error or off")
    # Validate serialization before creating outputs.
    json.dumps(provenance, allow_nan=False)
    stem = Path(stem)
    targets = [Path(str(stem) + suffix) for suffix in (".pdf", ".png", ".export.json")]
    for path in targets:
        if path.is_symlink() or (path.exists() and not overwrite):
            raise FileExistsError(f"Refusing to replace {path}; use a new stem or explicit overwrite")
    stem.parent.mkdir(parents=True, exist_ok=True)
    warnings = layout_warnings(fig)
    if collision_mode == 'off':
        collisions = {'status': 'skipped', 'reason': 'Disabled explicitly by caller'}
    else:
        from layout_audit import audit_layout
        collisions = audit_layout(fig)
        if collision_mode == 'error' and collisions['status'] != 'screen_pass':
            raise ValueError('Layout review required before export; run audit_layout for findings and skipped checks')
    manifest = {
        "schema_version": 1, "size_mm": [width_mm, height_mm], "png_dpi": dpi,
        "python": platform.python_version(), "matplotlib": mpl.__version__,
        "provenance": provenance or {}, "layout_warnings": warnings,
        "collision_audit": collisions,
        "limitations": "Geometry screening only; review PNG and rendered PDF. No palette approval or journal certification.",
        "files": {},
    }
    with tempfile.TemporaryDirectory(prefix=".figure-", dir=stem.parent) as temporary:
        staged = [Path(temporary) / path.name for path in targets]
        # bbox_inches=None alone still consults rcParams['savefig.bbox'].
        with mpl.rc_context({"savefig.bbox": None, "pdf.fonttype": 42, "ps.fonttype": 42}):
            for path in staged[:2]:
                fig.savefig(path, dpi=dpi, bbox_inches=None, transparent=False,
                            facecolor=fig.get_facecolor(), edgecolor=fig.get_edgecolor())
                manifest["files"][path.suffix[1:]] = {
                    "name": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        staged[2].write_text(json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
        for source, target in zip(staged, targets):
            if target.is_symlink() or (target.exists() and not overwrite):
                raise FileExistsError(f"Output appeared while rendering: {target}")
            os.replace(source, target)
    return manifest
