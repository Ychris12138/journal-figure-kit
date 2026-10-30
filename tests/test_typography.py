from pathlib import Path
import json
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/journal-matplotlib/scripts'))
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from typography import resolve_typography, tag_text, PRESETS
from audit_placement import audit_placement
from figure_export import export_pair


class TypographyTests(unittest.TestCase):
    def tearDown(self): plt.close('all')

    def test_inverse_reduction_and_absolute_overrides(self):
        p=resolve_typography('JCP',final_width_mm=85,canvas_width_mm=170,font_scale=1.1,
                             overrides={'legend':9})
        self.assertAlmostEqual(p.pt('body'),19.8)
        self.assertEqual(p.pt('legend'),18)
        self.assertAlmostEqual(p.final_pt['tick'],9.35)

    def test_validation(self):
        for args in ({'final_width_mm':0},{'final_width_mm':float('nan')},
                     {'final_width_mm':85,'font_scale':-1},
                     {'final_width_mm':85,'overrides':{'ticks':8}},
                     {'final_width_mm':85,'overrides':{'legend':True}}):
            with self.subTest(args=args),self.assertRaises(ValueError):
                resolve_typography('jcp',**args)

    def test_conflicts_warn_without_silent_clamping(self):
        p=resolve_typography('nature',final_width_mm=89,font_scale=1.2)
        self.assertAlmostEqual(p.final_pt['label'],8.4)
        self.assertTrue(any('exceeds' in w for w in p.warnings()))
        self.assertTrue(any('panel=' in w for w in p.warnings()))
        self.assertTrue(any('below' in w for w in resolve_typography('jcp',final_width_mm=85,overrides={'tick':6}).warnings()))

    def test_all_profiles_sources_and_status(self):
        for key in json.loads(PRESETS.read_text())['profiles']:
            p=resolve_typography(key,final_width_mm=90)
            self.assertTrue(p.to_dict()['sources'])
            self.assertTrue(all(v>0 for v in p.final_pt.values()))
        self.assertTrue(any('glyph' in w for w in resolve_typography('prl',final_width_mm=85).warnings()))
        self.assertTrue(any('Draft only' in w for w in resolve_typography('science',final_width_mm=90).warnings()))

    def test_existing_artists_idempotence_data_palette_and_global_state(self):
        before=mpl.rcParams.copy()
        p=resolve_typography('jcp',final_width_mm=85,overrides={'panel':11,'annotation':8,'colorbar_tick':9})
        fig,ax=plt.subplots(figsize=(85/25.4,75/25.4),layout='constrained')
        line,=ax.plot([0,1],[2,3],color='#0072B2',label='State')
        mesh=ax.imshow([[1,2],[3,4]],extent=(0,1,2,3),alpha=.4)
        cb=fig.colorbar(mesh,ax=ax); cb.set_label('Energy')
        ax.set(xlabel='Time',ylabel='Signal',title='Example')
        lg=ax.legend(title='Legend'); flg=fig.legend([line],['Figure legend'])
        note=ax.text(.1,.5,'Note',transform=ax.transAxes)
        panel=tag_text(ax.text(.02,.95,'(a)',transform=ax.transAxes),'panel')
        arr=mesh.get_array().copy(); cmap=mesh.get_cmap(); norm=(mesh.norm.vmin,mesh.norm.vmax)
        report=p.apply(fig,colorbars=[cb]); p.apply(fig,colorbars=[cb])
        self.assertEqual(panel.get_fontsize(),11)
        self.assertEqual(note.get_fontsize(),8)
        self.assertEqual(lg.get_texts()[0].get_fontsize(),8.5)
        self.assertEqual(flg.get_texts()[0].get_fontsize(),8.5)
        self.assertEqual(cb.ax.get_yticklabels()[0].get_fontsize(),9)
        ax.set_xlim(-100,100); p.apply(fig,colorbars=[cb])
        self.assertTrue(all(t.get_fontsize()==8.5 for t in ax.get_xticklabels()))
        np.testing.assert_array_equal(line.get_ydata(),[2,3]); np.testing.assert_array_equal(arr,mesh.get_array())
        self.assertEqual(line.get_color(),'#0072B2'); self.assertIs(mesh.get_cmap(),cmap)
        self.assertEqual((mesh.norm.vmin,mesh.norm.vmax),norm)
        self.assertEqual(mpl.rcParams,before)
        self.assertTrue(any(t['role']=='panel' for t in report['texts']))

    def test_pdf_effective_size_and_math_span_detection(self):
        p=resolve_typography('jpcl',final_width_mm=85,canvas_width_mm=170)
        with tempfile.TemporaryDirectory() as tmp:
            fig=plt.figure(figsize=(170/25.4,60/25.4))
            fig.text(.1,.5,'Readable text',fontsize=p.pt('body'))
            export_pair(fig,Path(tmp)/'figure',width_mm=170,height_mm=60)
            a=audit_placement(Path(tmp)/'figure.pdf',final_width_mm=85,min_font_pt=7)
            self.assertEqual(a['final_pt_histogram'],{8.0:1})
            self.assertEqual(a['warnings'],[])
            tiny=audit_placement(Path(tmp)/'figure.pdf',final_width_mm=42.5,min_font_pt=7)
            self.assertEqual(tiny['final_pt_histogram'],{4.0:1})
            self.assertEqual(len(tiny['below']),1)

    def test_canvas_mismatch(self):
        fig=plt.figure(figsize=(4,3))
        with self.assertRaises(ValueError): resolve_typography('nature',final_width_mm=89).apply(fig)

    def test_no_extractable_text_is_not_a_pass(self):
        import pymupdf
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'blank.pdf'; d=pymupdf.open(); d.new_page();d.save(p);d.close()
            report=audit_placement(p,final_width_mm=85)
            self.assertEqual(report['span_count'],0)
            self.assertTrue(report['warnings'])

    def test_pdf_userunit_effective_font_and_width(self):
        from pypdf import PdfReader,PdfWriter
        from pypdf.generic import NameObject,NumberObject
        with tempfile.TemporaryDirectory() as tmp:
            fig=plt.figure(figsize=(85/25.4,50/25.4));fig.text(.2,.5,'Test',fontsize=8)
            export_pair(fig,Path(tmp)/'base',width_mm=85,height_mm=50)
            reader=PdfReader(Path(tmp)/'base.pdf');writer=PdfWriter();page=reader.pages[0]
            page[NameObject('/UserUnit')]=NumberObject(2);writer.add_page(page)
            with (Path(tmp)/'unit.pdf').open('wb') as f:writer.write(f)
            report=audit_placement(Path(tmp)/'unit.pdf',final_width_mm=85)
            self.assertAlmostEqual(report['source_size_mm'][0],170,places=3)
            self.assertEqual(report['final_pt_histogram'],{8.0:1})


if __name__=='__main__': unittest.main()
