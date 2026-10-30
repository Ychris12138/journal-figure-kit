"""Synthetic collision failures and repairs; no research data or palette approval."""
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/journal-matplotlib/scripts'))
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pymupdf
from PIL import Image,ImageDraw
from layout_audit import audit_layout,reflow_layout,place_legend,place_axes_note,reserved_legend,allow_data_overlay,save_overlay
from figure_export import export_pair


def main(output):
    out=Path(output);out.mkdir(parents=True,exist_ok=False)
    records=[]
    def save(fig,name):
        fig.canvas.draw();report=audit_layout(fig)
        w,h=fig.get_size_inches()*25.4
        export_pair(fig,out/name,width_mm=float(w),height_mm=float(h),provenance={'synthetic':True})
        save_overlay(fig,report,out/(name+'-audit.png'))
        with pymupdf.open(out/(name+'.pdf')) as doc:
            doc[0].get_pixmap(matrix=pymupdf.Matrix(1.8,1.8)).save(out/(name+'-pdf.png'))
        return report
    with mpl.rc_context({'font.family':'DejaVu Sans','font.size':8,'axes.titlesize':9,'legend.fontsize':8,'pdf.fonttype':42}):
        fig,ax=plt.subplots(figsize=(89/25.4,65/25.4),layout='constrained')
        x=np.linspace(0,1,100);ax.plot(x,.94-.01*x,color='#333333',label='Observed state')
        ax.set(xlim=(0,1),ylim=(0,1),xlabel='Distance (nm)',ylabel='Response')
        ax.legend(loc='upper right',framealpha=1)
        before=save(fig,'legend-before');repair=place_legend(ax);after=save(fig,'legend-after')
        records.append(dict(case='Opaque legend hides a line',before=before,after=after,repair=repair['status']));plt.close(fig)

        def dense(reserved=False):
            fig=plt.figure(figsize=(89/25.4,75/25.4),layout='constrained')
            gs=fig.add_gridspec(2 if reserved else 1,1,height_ratios=[1,.15] if reserved else [1])
            ax=fig.add_subplot(gs[0]);bars=ax.bar(np.arange(10),np.ones(10),width=1,color='#888888',label='Synthetic plateau')
            ax.set(xlim=(-.5,9.5),ylim=(0,1),xlabel='Bin',ylabel='Density')
            if reserved:reserved_legend(fig.add_subplot(gs[1]),[bars],['Synthetic plateau'],frameon=False)
            else:ax.legend(loc='upper right')
            return fig,ax
        fig,ax=dense();before=save(fig,'dense-before');attempt=place_legend(ax);plt.close(fig)
        fig,ax=dense(True);after=save(fig,'dense-after');plt.close(fig)
        records.append(dict(case='Dense plot needs a reserved key',before=before,after=after,repair=attempt['status']+' -> GridSpec key row'))

        fig,axs=plt.subplots(2,2,figsize=(178/25.4,110/25.4));fig.subplots_adjust(hspace=0,wspace=0)
        for i,ax in enumerate(axs.flat):
            ax.plot([0,1],[.2,.8],color='#333333');ax.set(xlabel='Lag time (ps)',ylabel='Normalized response',title=f'Condition {i+1}')
        before=save(fig,'panels-before');reflow_layout(fig);after=save(fig,'panels-after');plt.close(fig)
        records.append(dict(case='Axis labels and panel titles collide',before=before,after=after,repair='Constrained GridSpec reflow'))

        fig,ax=plt.subplots(figsize=(89/25.4,65/25.4),layout='constrained')
        ax.bar([0,1,2],[1,2,1.5],color='#888888');ax.set_xticks([0,1,2],['Low pressure 221 K','High pressure 210 K','Reference state'])
        ax.set(ylabel='Response')
        before=save(fig,'ticks-before')
        ax.set_xticks([0,1,2],['Low pressure\n221 K','High pressure\n210 K','Reference\nstate'])
        after=save(fig,'ticks-after');plt.close(fig)
        records.append(dict(case='Long categorical tick labels',before=before,after=after,repair='Wrap complete labels; same tick positions and words'))

        fig,ax=plt.subplots(figsize=(89/25.4,65/25.4),layout='constrained')
        ax.plot([0,1],[.2,.2],color='#333333');ax.set(ylim=(0,1),xlabel='Time (ps)',ylabel='Response',title='Relaxation')
        note=ax.text(.5,1.03,'Fit: tau = 2.0 ps',ha='center',va='bottom',transform=ax.transAxes)
        before=save(fig,'title-before');repair=place_axes_note(note);after=save(fig,'title-after');plt.close(fig)
        records.append(dict(case='Title and free note collide',before=before,after=after,repair=repair['status']))

        fig,ax=plt.subplots(figsize=(89/25.4,65/25.4),layout='constrained')
        im=ax.imshow([[1,2],[3,4]],cmap='Greys');fig.colorbar(im,ax=ax,label='Synthetic value')
        for i in range(2):
            for j in range(2):allow_data_overlay(ax.text(j,i,str(1+i*2+j),ha='center',va='center',color='white' if i else 'black'),'Numeric value intentionally in its own heatmap cell')
        result=save(fig,'heatmap-intentional');plt.close(fig)
        records.append(dict(case='Intentional heatmap values (negative control)',before=result,after=result,repair='Scoped data-overlay declaration; text-text checks remain active'))
    (out/'results.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
    proof=pymupdf.open()
    for stem,title in [('legend','Opaque legend'),('dense','Dense bars'),('panels','Panel decorations'),('ticks','Long tick labels'),('title','Title and note')]:
        page=proof.new_page(width=660,height=750 if stem=='panels' else 310)
        page.insert_text((20,24),title+' - before / after (synthetic)',fontsize=13)
        for i,phase in enumerate(['before','after']):
            src=pymupdf.open(out/(stem+'-'+phase+'.pdf'))
            box=pymupdf.Rect(20,45+i*350,640,370+i*350) if stem=='panels' else pymupdf.Rect(20+i*325,45,315+i*325,page.rect.height-15)
            page.show_pdf_page(box,src,0)
        page.get_pixmap(matrix=pymupdf.Matrix(1.5,1.5)).save(out/(stem+'-comparison.png'))
    proof.save(out/'layout-comparison.pdf')
    print(json.dumps([dict(case=r['case'],before=len(r['before']['findings']),after=len(r['after']['findings']),skipped=r['after']['skipped']) for r in records],indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True);main(p.parse_args().output)
