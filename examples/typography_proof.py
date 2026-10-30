"""Synthetic font reduction proof. No experimental data or palette approvals."""
from pathlib import Path
import argparse, json, sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/journal-matplotlib/scripts'))
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pymupdf as fitz
from typography import resolve_typography, tag_text
from figure_export import export_pair
from audit_placement import audit_placement


def main(output):
    out=Path(output); out.mkdir(parents=True,exist_ok=False)
    cases=[('oversized-uncompensated',170,100,None),
           ('jcp-final',85,62,resolve_typography('jcp',final_width_mm=85)),
           ('jcp-larger-10pct',85,62,resolve_typography('jcp',final_width_mm=85,font_scale=1.1)),
           ('jcp-compensated',170,124,resolve_typography('jcp',final_width_mm=85,canvas_width_mm=170))]
    results=[]
    for name,w,h,fonts in cases:
        rc={'font.family':'DejaVu Sans','font.size':8,'axes.labelsize':8,
            'axes.titlesize':8,'xtick.labelsize':8,'ytick.labelsize':8,
            'legend.fontsize':8,'legend.frameon':False,'pdf.fonttype':42}
        with mpl.rc_context({**rc,**(fonts.rc() if fonts else {})}):
            fig,ax=plt.subplots(figsize=(w/25.4,h/25.4),layout='constrained')
            x=np.linspace(0,5,60); ax.plot(x,np.exp(-x),color='#333333',label='Synthetic decay')
            ax.set(xlabel='Time (a.u.)',ylabel='Response (a.u.)')
            ax.legend(loc='upper right'); ax.text(.6,.65,'Synthetic only',transform=ax.transAxes)
            tag_text(ax.text(.03,.95,'(a)',va='top',transform=ax.transAxes),'panel')
            provenance={'synthetic':True}
            if fonts: provenance['typography']=fonts.apply(fig)
            export_pair(fig,out/name,width_mm=w,height_mm=h,provenance=provenance)
            plt.close(fig)
        results.append({'id':name,**audit_placement(out/(name+'.pdf'),final_width_mm=85,min_font_pt=8)})
    # A4 proof contains figures at exactly 85 mm, never fit-to-cell enlarged.
    proof=fitz.open(); page=proof.new_page(width=210/25.4*72,height=297/25.4*72)
    page.insert_text((28,28),'Typography at 85 mm placement - synthetic proof',fontsize=12)
    for i,(name,_,_,_) in enumerate(cases):
        src=fitz.open(out/(name+'.pdf')); x=(12+102*(i%2))*72/25.4; y=(25+103*(i//2))*72/25.4
        page.insert_text((x,y-7),name,fontsize=8)
        height=src[0].rect.height*(85*72/25.4)/src[0].rect.width
        page.show_pdf_page(fitz.Rect(x,y,x+85*72/25.4,y+height),src,0)
    page.insert_text((28,700),'Print at 100%. Screen fit-to-window is not physical size. Grayscale synthetic data.',fontsize=8)
    proof.save(out/'proof-a4.pdf')
    page.get_pixmap(matrix=fitz.Matrix(1.7,1.7)).save(out/'proof-a4.png')
    (out/'metrics.json').write_text(json.dumps(results,indent=2),encoding='utf-8')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--output',required=True)
    main(p.parse_args().output)
