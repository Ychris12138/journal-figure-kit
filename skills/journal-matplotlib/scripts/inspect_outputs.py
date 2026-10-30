#!/usr/bin/env python3
"""Measure exported figures. Exit 0 pass, 1 review/skip, 2 missing/invalid/size failure."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

MODE_DPI = {"explore": 180, "report": 300, "publication": 600}


def message(result, level, code, detail):
    result[level].append({"code": code, "detail": detail})


def compare_size(result, actual, target, tolerance, label):
    if not actual:
        return
    for i, axis in enumerate(("width", "height")):
        if target[i] is not None and abs(actual[i] - target[i]) > tolerance:
            message(result, "errors", "size_mismatch",
                    f"{label} {axis} {actual[i]:.3f} mm != {target[i]:.3f} mm")


def inspect_png(path, result, options, target):
    try:
        from PIL import Image, ImageChops, ImageColor
    except ImportError:
        message(result, "warnings", "skipped_png", "Install Pillow for PNG metadata/margins.")
        return
    with Image.open(path) as source:
        source.load()
        dpi = source.info.get("dpi")
        result["png"] = {"pixels": list(source.size), "dpi": list(dpi) if dpi else None}
        valid_dpi = dpi and len(dpi) == 2 and all(math.isfinite(v) and v > 0 for v in dpi)
        if not valid_dpi:
            message(result, "warnings", "unknown_dpi", "PNG has no valid DPI; physical size/margins skipped.")
            if any(v is not None for v in target):
                message(result, "errors", "unverifiable_size", "PNG exact physical size cannot be verified.")
        else:
            size = [source.size[i] * 25.4 / dpi[i] for i in (0, 1)]
            result["png"]["size_mm"] = size
            compare_size(result, size, target, options.tolerance_mm, "PNG")
            if min(dpi) + 1 < options.dpi:
                message(result, "warnings", "low_dpi", f"PNG {min(dpi):.1f} < target {options.dpi:g} dpi.")
        rgba = source.convert("RGBA")
        if rgba.getchannel("A").getextrema()[0] < 255:
            message(result, "warnings", "transparency",
                    f"PNG has transparency; margins composited on {options.background}.")
        background = ImageColor.getrgb(options.background)
        result["png"]["margin_background"] = options.background
        rgb = Image.alpha_composite(Image.new("RGBA", rgba.size, background+(255,)), rgba).convert("RGB")
        difference = ImageChops.difference(rgb, Image.new("RGB", rgb.size, background))
        channels = difference.split()
        maximum = ImageChops.lighter(ImageChops.lighter(channels[0], channels[1]), channels[2])
        mask = maximum.point(lambda p: 255 if p > options.white_threshold else 0)
        box = mask.getbbox()
        if box is None:
            message(result, "errors", "blank_image", "No content detected against specified background.")
            return
        w, h = rgb.size
        margins_px = [box[0], box[1], w - box[2], h - box[3]]
        fractions = [margins_px[i] / (w if i % 2 == 0 else h) for i in range(4)]
        names = ("left", "top", "right", "bottom")
        result["png"]["outer_margins_fraction"] = dict(zip(names, fractions))
        if valid_dpi:
            margins_mm = [margins_px[i] * 25.4 / dpi[i % 2] for i in range(4)]
            result["png"]["outer_margins_mm"] = dict(zip(names, margins_mm))
            for name, mm, fraction in zip(names, margins_mm, fractions):
                if mm > options.margin_mm and fraction > options.margin_fraction:
                    message(result, "warnings", "outer_whitespace",
                            f"{name}: {mm:.2f} mm ({fraction:.1%}); review source layout.")
        if any(m <= 1 for m in margins_px):
            message(result, "warnings", "edge_contact",
                    "Artwork touches/approaches a canvas edge; check clipping or intended full bleed.")


def dereference(value):
    return value.get_object() if hasattr(value, "get_object") else value


def pdf_resources(resources, seen, fonts, images):
    resources = dereference(resources) or {}
    key = id(resources)
    if key in seen:
        return
    seen.add(key)
    for raw in (dereference(resources.get("/Font")) or {}).values():
        font = dereference(raw)
        name = str(font.get("/BaseFont", "(unnamed)"))
        subtype = str(font.get("/Subtype", ""))
        leaves = dereference(font.get("/DescendantFonts")) or [font]
        embedded = []
        for raw_leaf in leaves:
            leaf = dereference(raw_leaf)
            descriptor = dereference(leaf.get("/FontDescriptor")) or {}
            embedded.append(any(descriptor.get(k) is not None for k in ("/FontFile", "/FontFile2", "/FontFile3")))
        fonts[(name, subtype)] = {"name": name, "subtype": subtype, "embedded": all(embedded)}
    for raw in (dereference(resources.get("/XObject")) or {}).values():
        obj = dereference(raw)
        if obj.get("/Subtype") == "/Image":
            images.add(id(obj))
        elif obj.get("/Subtype") == "/Form":
            pdf_resources(obj.get("/Resources"), seen, fonts, images)


def inspect_pdf(path, result, options, target):
    try:
        from pypdf import PdfReader
    except ImportError:
        message(result, "warnings", "skipped_pdf_structure", "Install pypdf for page dimensions/font embedding.")
    else:
        reader = PdfReader(path)
        sizes, fonts, images, seen = [], {}, set(), set()
        if len(reader.pages) != 1:
            message(result, "errors", "page_count", f"Expected one figure page; found {len(reader.pages)}.")
        for page in reader.pages:
            unit = float(page.get("/UserUnit", 1))
            if not math.isfinite(unit) or unit <= 0:
                raise ValueError("Invalid PDF UserUnit")
            size = [float(page.mediabox.width) * unit * 25.4 / 72, float(page.mediabox.height) * unit * 25.4 / 72]
            sizes.append(size)
            compare_size(result, size, target, options.tolerance_mm, "PDF MediaBox")
            if list(page.cropbox) != list(page.mediabox):
                message(result, "warnings", "cropbox_differs", "PDF CropBox differs from MediaBox; inspect displayed size.")
            if int(page.get("/Rotate", 0)) % 360:
                message(result, "warnings", "rotated_page", "PDF page rotation may swap displayed dimensions.")
            pdf_resources(page.get("/Resources"), seen, fonts, images)
        result["pdf"] = {"pages": len(reader.pages), "size_mm": sizes,
                         "fonts": list(fonts.values()), "image_resources": len(images)}
        if not fonts:
            message(result, "warnings", "no_fonts", "No PDF fonts; text may be absent, outlined or rasterized.")
        for font in fonts.values():
            if font["subtype"] == "/Type3":
                message(result, "warnings", "type3_font", f"{font['name']}: check text editability.")
            elif not font["embedded"]:
                message(result, "warnings", "unembedded_font", font["name"])
        if sizes and result.get("png", {}).get("size_mm"):
            png_size = result["png"]["size_mm"]
            compare_size(result, sizes[0], png_size, options.tolerance_mm, "PDF vs PNG")
    try:
        import pymupdf
    except ImportError:
        message(result, "warnings", "skipped_pdf_text", "Install PyMuPDF for rendered text/raster metrics.")
        return
    with pymupdf.open(path) as document:
        text_sizes, raster_dpi = [], []
        for page in document:
            for block in page.get_text("dict")["blocks"]:
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        if not span["text"].strip():
                            continue
                        text_sizes.append(span["size"])
                        box = pymupdf.Rect(span["bbox"])
                        if not (page.rect + (-0.5, -0.5, 0.5, 0.5)).contains(box):
                            message(result, "warnings", "text_near_crop", span["text"][:60])
            for item in page.get_image_info():
                a, b, c, d, _, _ = item["transform"]
                xpt, ypt = math.hypot(a, b), math.hypot(c, d)
                if xpt > 0 and ypt > 0:
                    effective = min(item["width"] * 72 / xpt, item["height"] * 72 / ypt)
                    raster_dpi.append(effective)
        result["pdf_text"] = {"min_pt": min(text_sizes) if text_sizes else None,
                              "max_pt": max(text_sizes) if text_sizes else None}
        result["pdf_raster_min_dpi"] = min(raster_dpi) if raster_dpi else None
        if not text_sizes:
            message(result, "warnings", "no_extractable_text", "PDF has no extractable text; inspect editability.")
        elif options.min_font_pt is not None and min(text_sizes) + 0.05 < options.min_font_pt:
            message(result, "warnings", "small_text",
                    f"Minimum {min(text_sizes):.2f} pt; target {options.min_font_pt:g}. Inspect math subscripts too.")
        if text_sizes and options.max_font_pt is not None and max(text_sizes) - 0.05 > options.max_font_pt:
            message(result, "warnings", "large_text", f"Maximum {max(text_sizes):.2f} pt; include panel labels in bounds.")
        if raster_dpi and options.raster_dpi and min(raster_dpi) + 1 < options.raster_dpi:
            message(result, "warnings", "low_embedded_raster_dpi",
                    f"Minimum placed raster {min(raster_dpi):.1f} dpi; target {options.raster_dpi:g}.")


def inspect_stem(stem, options, target=(None, None)):
    result = {"stem": str(stem), "warnings": [], "errors": []}
    suffixes = [".png"] if options.mode == "explore" else [".png", ".pdf"]
    for suffix in suffixes:
        path = Path(str(stem) + suffix)
        if not path.is_file():
            message(result, "errors", "missing_file", str(path))
            continue
        try:
            (inspect_png if suffix == ".png" else inspect_pdf)(path, result, options, target)
        except Exception as error:
            message(result, "errors", "invalid_file", f"{path.name}: {type(error).__name__}: {error}")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_stem", type=Path, help="Path WITHOUT the .png/.pdf suffix")
    parser.add_argument("--mode", choices=MODE_DPI, default="publication")
    parser.add_argument("--width-mm", type=float)
    parser.add_argument("--height-mm", type=float)
    parser.add_argument("--dpi", type=float, help="PNG target; overrides mode default")
    parser.add_argument("--raster-dpi", type=float, help="Optional minimum placed image DPI inside PDF")
    parser.add_argument("--min-font-pt", type=float)
    parser.add_argument("--max-font-pt", type=float)
    parser.add_argument("--tolerance-mm", type=float, default=0.25)
    parser.add_argument("--margin-mm", type=float, default=4, help="Outer-edge warning threshold; requires fraction too")
    parser.add_argument("--margin-fraction", type=float, default=0.05, help="Outer-edge fraction threshold; local heuristic")
    parser.add_argument("--white-threshold", type=int, default=8, help="RGB distance from white (0..254)")
    parser.add_argument("--background", default="#FFFFFF", help="Six-digit HEX canvas background for margin screening")
    parser.add_argument("--panels-dir", type=Path)
    parser.add_argument("--expected-panels", type=int)
    parser.add_argument("--json", type=Path, help="Write measured facts and machine-readable warnings/errors")
    options = parser.parse_args(argv)
    import re
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", options.background):
        parser.error("background must be a six-digit HEX color")
    if options.dpi is None:
        options.dpi = MODE_DPI[options.mode]
    for name in ("width_mm", "height_mm", "dpi", "raster_dpi", "min_font_pt", "max_font_pt"):
        value = getattr(options, name)
        if value is not None and (not math.isfinite(value) or value <= 0):
            parser.error(f"--{name.replace('_', '-')} must be finite and positive")
    if not (0 <= options.white_threshold <= 254 and 0 <= options.margin_fraction < 1):
        parser.error("invalid white threshold or margin fraction")
    if not math.isfinite(options.margin_mm) or options.margin_mm < 0:
        parser.error("margin-mm must be finite and nonnegative")
    if not math.isfinite(options.tolerance_mm) or options.tolerance_mm < 0:
        parser.error("tolerance-mm must be finite and nonnegative")
    if options.min_font_pt and options.max_font_pt and options.min_font_pt > options.max_font_pt:
        parser.error("font minimum exceeds maximum")
    if options.expected_panels is not None and (options.expected_panels < 1 or not options.panels_dir):
        parser.error("expected-panels requires a panels-dir and a positive count")
    report = {"schema_version": 1, "mode": options.mode,
              "target_mm": [options.width_mm, options.height_mm],
              "limitations": "Uniform-background outer padding only; no guarantee of no overlaps/clipping or full journal compliance.",
              "figures": [inspect_stem(options.output_stem, options, (options.width_mm, options.height_mm))]}
    if options.panels_dir:
        if not options.panels_dir.is_dir():
            report["figures"].append({"stem": str(options.panels_dir), "warnings": [],
                                     "errors": [{"code": "missing_panel_directory", "detail": str(options.panels_dir)}]})
        else:
            panels = sorted({p.with_suffix("") for p in options.panels_dir.iterdir()
                             if p.is_file() and p.suffix.lower() in (".png", ".pdf")})
            if not panels or (options.expected_panels is not None and len(panels) != options.expected_panels):
                report["figures"].append({"stem": str(options.panels_dir), "warnings": [],
                    "errors": [{"code": "panel_count", "detail": f"Found {len(panels)}; expected {options.expected_panels or 'at least one'}."}]})
            # Do not impose overview dimensions on standalone figures.
            report["figures"].extend(inspect_stem(stem, options) for stem in panels)
    errors = sum(len(f["errors"]) for f in report["figures"])
    warnings = sum(len(f["warnings"]) for f in report["figures"])
    report["exit_code"] = 2 if errors else 1 if warnings else 0
    if options.json:
        options.json.parent.mkdir(parents=True, exist_ok=True)
        options.json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    for result in report["figures"]:
        print(result["stem"])
        if result.get("png"):
            print("  PNG:", json.dumps(result["png"], ensure_ascii=False))
        if result.get("pdf"):
            print("  PDF:", json.dumps(result["pdf"], ensure_ascii=False))
        for level in ("warnings", "errors"):
            for item in result[level]:
                print(f"  {level.upper()} {item['code']}: {item['detail']}")
    print(f"Automated result: {errors} errors; {warnings} warnings. Visual inspection still required.")
    return report["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
