"""Measure PDF text at a specified manuscript placement width, without editing it."""
import argparse
from collections import Counter
import json
from pathlib import Path

from typography import positive


def audit_placement(pdf, *, final_width_mm, min_font_pt=None, max_font_pt=None):
    import pymupdf
    width = positive(final_width_mm, 'final_width_mm')
    if min_font_pt is not None: positive(min_font_pt, 'min_font_pt')
    if max_font_pt is not None: positive(max_font_pt, 'max_font_pt')
    if min_font_pt is not None and max_font_pt is not None and min_font_pt > max_font_pt:
        raise ValueError('min_font_pt exceeds max_font_pt')
    with pymupdf.open(pdf) as doc:
        if len(doc) != 1: raise ValueError('Expected one figure per PDF; select a single-page figure')
        page=doc[0]
        # PyMuPDF page.rect and extracted span sizes reflect PDF UserUnit.
        source_width=page.rect.width * 25.4 / 72
        reduction=width/source_width
        texts=[]
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines',[]):
                for span in line['spans']:
                    if span['text'].strip():
                        texts.append(dict(text=span['text'],font=span['font'],
                                          source_pt=span['size'],final_pt=span['size']*reduction,
                                          bbox=span['bbox']))
        warnings=[]
        if not texts: warnings.append('No extractable text: raster/outlined text cannot be assessed by this tool')
        below=[t for t in texts if min_font_pt is not None and t['final_pt'] < min_font_pt-.02]
        above=[t for t in texts if max_font_pt is not None and t['final_pt'] > max_font_pt+.02]
        if below: warnings.append(f'{len(below)} text spans below requested minimum at placement size; inspect math subscripts separately')
        if above: warnings.append(f'{len(above)} text spans above requested maximum; inspect panel-label exceptions separately')
        return dict(source_pdf=str(Path(pdf)),source_size_mm=[source_width,page.rect.height*25.4/72],
                    final_size_mm=[width,page.rect.height*25.4/72*reduction],reduction=reduction,
                    span_count=len(texts),
                    final_pt_histogram=dict(sorted(Counter(round(t['final_pt'],2) for t in texts).items())),
                    below=below,above=above,warnings=warnings,
                    limitation='Nominal extracted PDF span sizes under uniform placement. Not glyph ink height, full visibility, raster text, overlap or journal certification. Verify actual manuscript placement; browser zoom is not print scale.')


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('pdf',type=Path)
    p.add_argument('--final-width-mm',required=True,type=float)
    p.add_argument('--min-font-pt',type=float)
    p.add_argument('--max-font-pt',type=float)
    p.add_argument('--json',type=Path)
    a=p.parse_args()
    try:
        result=audit_placement(a.pdf,final_width_mm=a.final_width_mm,
                               min_font_pt=a.min_font_pt,max_font_pt=a.max_font_pt)
        text=json.dumps(result,ensure_ascii=False,indent=2)
        if a.json:
            a.json.parent.mkdir(parents=True,exist_ok=True)
            with a.json.open('x',encoding='utf-8') as f: f.write(text+'\n')
        print(text)
    except (ValueError,OSError,ImportError) as e: p.error(str(e))
    raise SystemExit(1 if result['warnings'] else 0)
