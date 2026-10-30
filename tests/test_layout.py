from pathlib import Path
import json,sys,tempfile,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/journal-matplotlib/scripts'))
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import layout_audit as la


def codes(report):return {x['code'] for x in report['findings']}


class LayoutTests(unittest.TestCase):
    def tearDown(self):plt.close('all')

    def test_hidden_curve_under_opaque_legend_detected_and_repaired(self):
        fig,ax=plt.subplots(figsize=(4,3),layout='constrained')
        x=np.linspace(0,1,100);line,=ax.plot(x,.94-.01*x,label='Measured')
        ax.set(xlim=(0,1),ylim=(0,1));legend=ax.legend(loc='upper right',framealpha=1)
        before=la.audit_layout(fig)
        self.assertIn('data_overlap',codes(before))
        olddata=line.get_xydata().copy();oldtext=[t.get_text() for t in legend.texts]
        repair=la.place_legend(ax)
        self.assertEqual(repair['status'],'placed')
        self.assertEqual(oldtext,[t.get_text() for t in legend.texts])
        np.testing.assert_array_equal(olddata,line.get_xydata())
        self.assertFalse(any(f['code'].startswith('data_') and any(i.startswith('legend') for i in f['items']) for f in repair['after']['findings']))

    def test_sparse_segment_crossing_is_not_just_vertex_test(self):
        fig,ax=plt.subplots();ax.set(xlim=(0,1),ylim=(0,1))
        ax.plot([0,1],[.5,.5]);ax.text(.5,.5,'Crossing',ha='center',va='center')
        self.assertIn('data_overlap',codes(la.audit_layout(fig)))

    def test_nan_gap_does_not_become_data_rectangle(self):
        fig,ax=plt.subplots();ax.set(xlim=(0,1),ylim=(0,1))
        ax.plot([0,.2,.5,.8,1],[.5,.5,np.nan,.5,.5])
        ax.text(.5,.5,'Gap',ha='center',va='center')
        self.assertNotIn('data_overlap',codes(la.audit_layout(fig)))

    def test_bar_band_and_marker_edges_count_as_data(self):
        builders=[lambda ax:ax.bar([.5],[.8],width=.4),
                  lambda ax:ax.fill_between([.2,.8],.2,.8,alpha=.2),
                  lambda ax:ax.scatter([.5],[.5],s=1000),
                  lambda ax:ax.errorbar([.5],[.5],yerr=.3,fmt='o',capsize=4)]
        for build in builders:
            fig,ax=plt.subplots();ax.set(xlim=(0,1),ylim=(0,1));build(ax)
            ax.text(.5,.5,'Label',ha='center',va='center')
            self.assertIn('data_overlap',codes(la.audit_layout(fig)))

    def test_off_canvas_and_text_collisions(self):
        fig,ax=plt.subplots();ax.text(.5,.5,'First');ax.text(.5,.5,'Second');fig.text(1.02,.8,'Outside')
        report=la.audit_layout(fig)
        self.assertIn('decoration_overlap',codes(report));self.assertIn('off_canvas',codes(report))

    def test_heatmap_overlay_exemption_is_scoped(self):
        fig,ax=plt.subplots();ax.imshow([[1,2],[3,4]])
        t=ax.text(0,0,'1',ha='center',va='center');la.allow_data_overlay(t,'Numeric label for this heatmap cell')
        report=la.audit_layout(fig)
        self.assertNotIn('data_overlap',codes(report));self.assertEqual(len(report['exemptions']),1)
        ax.text(0,0,'duplicate',ha='center',va='center')
        self.assertIn('decoration_overlap',codes(la.audit_layout(fig)))
        with self.assertRaises(ValueError):la.allow_data_overlay(t,'')

    def test_crowded_ticks_axis_titles_and_neighbor_panel_reflow(self):
        fig,axs=plt.subplots(2,2,figsize=(5,4));fig.subplots_adjust(hspace=0,wspace=0)
        for ax in axs.flat:
            ax.plot([0,1],[0,1]);ax.set(xlabel='Distance (nm)',ylabel='Probability density',title='Condition')
        before=la.audit_layout(fig);self.assertIn('decoration_overlap',codes(before))
        fonts=[a.xaxis.label.get_fontsize() for a in axs.flat];size=fig.get_size_inches().copy()
        after=la.reflow_layout(fig)['audit']
        self.assertLess(len(after['findings']),len(before['findings']))
        self.assertEqual(fonts,[a.xaxis.label.get_fontsize() for a in axs.flat]);np.testing.assert_equal(size,fig.get_size_inches())

    def test_legend_no_solution_restores_location(self):
        fig,ax=plt.subplots();ax.imshow(np.ones((10,10)));ax.plot([0,1],label='Key');lg=ax.legend(loc='upper right')
        loc=lg._loc;anchor=lg._bbox_to_anchor
        result=la.place_legend(ax)
        self.assertEqual(result['status'],'needs_reserved_region');self.assertEqual(lg._loc,loc);self.assertIs(lg._bbox_to_anchor,anchor)

    def test_empty_reserved_region_keeps_all_identity_entries(self):
        fig=plt.figure(layout='constrained');gs=fig.add_gridspec(1,2,width_ratios=[3,1]);ax=fig.add_subplot(gs[0]);key=fig.add_subplot(gs[1])
        one,=ax.plot([1,2],label='Same name',color='red');two,=ax.plot([2,1],label='Same name',color='blue')
        legend=la.reserved_legend(key,[one,two],['Same name','Same name'])
        self.assertEqual(len(legend.texts),2)
        self.assertNotIn('data_overlap',codes(la.audit_layout(fig)))
        with self.assertRaises(ValueError):la.reserved_legend(ax,[one],['Key'])

    def test_current_legend_identity_with_same_text_extra_legend(self):
        fig,ax=plt.subplots(figsize=(4,3),layout='constrained')
        line,=ax.plot([0,1],[.9,.9],label='Same name')
        ax.set(xlim=(0,1),ylim=(0,1))
        extra=ax.legend([line],['Same name'],loc='lower left',fontsize=8)
        ax.add_artist(extra)
        current=ax.legend([line],['Same name'],loc='upper right',fontsize=8)
        result=la.place_legend(ax)
        self.assertEqual(result['status'],'placed')
        self.assertIs(ax.get_legend(),current)
        self.assertEqual(extra._loc,3)

    def test_render_restores_visibility_engine_canvas_and_rc(self):
        fig,ax=plt.subplots(layout='constrained');ax.plot([0,1]);t=ax.text(.3,.5,'Note');t.set_visible(False)
        fig.canvas.draw();canvas=fig.canvas;engine=fig.get_layout_engine();before=mpl.rcParams.copy()
        visibility=[(a,a.get_visible()) for a in fig.findobj()]
        la.audit_layout(fig)
        self.assertIs(fig.canvas,canvas);self.assertIs(fig.get_layout_engine(),engine);self.assertEqual(before,mpl.rcParams)
        self.assertTrue(all(a.get_visible()==v for a,v in visibility))

    def test_failure_restores_state(self):
        fig,ax=plt.subplots(layout='constrained');ax.plot([0,1]);canvas=fig.canvas;engine=fig.get_layout_engine()
        with patch.object(la,'_items',side_effect=RuntimeError('synthetic failure')),self.assertRaises(RuntimeError):la.audit_layout(fig)
        self.assertIs(fig.canvas,canvas);self.assertIs(fig.get_layout_engine(),engine)

    def test_mask_failure_restores_hidden_artists(self):
        fig,ax=plt.subplots();ax.plot([0,1]);ax.set_title('Title');fig.canvas.draw()
        canvas=fig.canvas;visibility=[(a,a.get_visible()) for a in fig.findobj()]
        with self.assertRaises(RuntimeError):
            with la._render_scene(fig) as (temporary,_):
                with patch.object(temporary,'draw',side_effect=RuntimeError('data render failed')):
                    la._data_mask(fig,temporary,la._axes(fig))
        self.assertIs(fig.canvas,canvas)
        self.assertTrue(all(a.get_visible()==v for a,v in visibility))

    def test_font_change_requires_new_audit(self):
        fig,ax=plt.subplots(figsize=(4,3),layout='constrained')
        ax.plot([0,1],[.85,.85],label='State');ax.set(xlim=(0,1),ylim=(0,1));lg=ax.legend(loc='upper right',fontsize=7)
        before=la.audit_layout(fig);self.assertNotIn('data_overlap',codes(before))
        for text in lg.get_texts():text.set_fontsize(26)
        self.assertIn('data_overlap',codes(la.audit_layout(fig)))

    def test_out_of_view_hidden_ticks_are_not_reported(self):
        fig,ax=plt.subplots();ax.set_xticks([-100,0,.5,1,100]);ax.set_xlim(0,1)
        report=la.audit_layout(fig)
        self.assertFalse(any(x['text'] in ('−100.0','100.0','−100','100') for x in report['items']))

    def test_manual_axes_not_silently_reflowed(self):
        fig=plt.figure();ax=fig.add_axes([.2,.2,.6,.6]);position=ax.get_position().bounds
        self.assertFalse(la.reflow_layout(fig)['changed']);self.assertEqual(ax.get_position().bounds,position)

    def test_title_note_collision_and_anchored_annotation_boundary(self):
        fig,ax=plt.subplots(layout='constrained');ax.plot([0,1],[.2,.2]);ax.set_ylim(0,1)
        ax.set_title('Title');note=ax.text(.5,1.03,'Fit parameters',ha='center',va='bottom',transform=ax.transAxes)
        self.assertIn('decoration_overlap',codes(la.audit_layout(fig)))
        self.assertEqual(la.place_axes_note(note)['status'],'placed')
        arrow=ax.annotate('Point',(.5,.2),xytext=(.5,.8),arrowprops={'arrowstyle':'->'})
        with self.assertRaises(ValueError):la.place_axes_note(arrow)

    def test_export_records_collision_and_strict_refuses_without_files(self):
        from figure_export import export_pair
        fig,ax=plt.subplots(figsize=(3,2));ax.text(.5,.5,'A');ax.text(.5,.5,'B')
        with tempfile.TemporaryDirectory() as tmp:
            stem=Path(tmp)/'strict'
            with self.assertRaises(ValueError):export_pair(fig,stem,width_mm=76.2,height_mm=50.8,collision_mode='error')
            self.assertEqual(list(Path(tmp).iterdir()),[])
            result=export_pair(fig,Path(tmp)/'draft',width_mm=76.2,height_mm=50.8)
            self.assertEqual(result['collision_audit']['status'],'review')
            skipped=export_pair(fig,Path(tmp)/'skip',width_mm=76.2,height_mm=50.8,collision_mode='off')
            self.assertEqual(skipped['collision_audit']['status'],'skipped')


if __name__=='__main__':unittest.main()
