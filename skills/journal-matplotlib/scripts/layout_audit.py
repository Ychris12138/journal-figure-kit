"""Rendered 2D collision screening and bounded layout repair.

Uses text/legend boxes and an isolated data-layer alpha mask, not data bounding
rectangles (which would invent collisions across gaps). No statistical changes,
font shrinking, limit expansion, legend deduplication or persistent rcParams.
"""
from __future__ import annotations
from contextlib import contextmanager
import json
import math
from pathlib import Path

PRESETS = Path(__file__).resolve().parents[1]/'references/layout-presets.json'


def _profile(mode):
    profiles=json.loads(PRESETS.read_text(encoding='utf-8'))['profiles']
    if mode not in profiles: raise ValueError(f'Unknown layout mode: {mode}')
    return profiles[mode]


def allow_data_overlay(artist, reason):
    """Document intentional overlay (e.g. a heatmap cell value).

    Suppresses only this artist's data-obstruction finding, never text-text,
    clipping or canvas checks. Do not use for an accidentally covering legend.
    """
    from matplotlib.text import Text
    if not isinstance(artist,Text): raise ValueError('Only intentional Text overlays may be annotated')
    if not isinstance(reason,str) or not reason.strip(): raise ValueError('A specific reason is required')
    artist._journal_overlay_reason=reason.strip()
    return artist


@contextmanager
def _render_scene(fig):
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    original_canvas=fig.canvas
    engine=fig.get_layout_engine()
    try:
        canvas=FigureCanvasAgg(fig)
        canvas.draw()
        fig.set_layout_engine('none')
        canvas.draw()
        yield canvas,canvas.get_renderer()
    finally:
        fig.set_layout_engine(engine if engine is not None else 'none')
        # Restore actual None without allowing global constrained-layout rc to enable it.
        if engine is None: fig._layout_engine=None
        fig.set_canvas(original_canvas)


def _axes(fig):
    from matplotlib.axes import Axes
    return [a for a in fig.findobj(match=Axes) if a.get_visible()]


def _items(fig,axes,renderer):
    import numpy as np
    from matplotlib.text import Text,Annotation
    from matplotlib.legend import Legend
    records=[];seen=set()
    def add(artist,role,owner=None):
        if id(artist) in seen or not artist.get_visible() or artist.get_alpha()==0: return
        if isinstance(artist,Text):
            if not artist.get_text().strip(): return
            if isinstance(artist,Annotation) and not artist._check_xy(renderer): return
            box=Text.get_window_extent(artist,renderer)  # exclude Annotation arrows
            label=artist.get_text()
        else: box=artist.get_window_extent(renderer);label=' | '.join(t.get_text() for t in artist.get_texts())
        if not np.isfinite(box.extents).all() or box.width<=0 or box.height<=0:return
        seen.add(id(artist));records.append(dict(id=f'{role}:{len(records)}',role=role,artist=artist,
                                               owner=owner,box=box.frozen(),text=label))
    for i,ax in enumerate(axes):
        owner=f'axes[{i}]'
        if ax.axison:
            for axis in (ax.xaxis,ax.yaxis):
                if not axis.get_visible():continue
                add(axis.label,'axis_label',owner);add(axis.get_offset_text(),'offset',owner)
                bounds=sorted(axis.get_view_interval())
                for tick in axis.get_major_ticks()+axis.get_minor_ticks():
                    if bounds[0]-1e-10<=tick.get_loc()<=bounds[1]+1e-10:
                        add(tick.label1,'tick',owner);add(tick.label2,'tick',owner)
        for title in (ax.title,ax._left_title,ax._right_title):add(title,'title',owner)
        for text in ax.texts:add(text,getattr(text,'_journal_font_role','annotation'),owner)
        for legend in ax.findobj(match=Legend):add(legend,'legend',owner)
    for text in fig.texts:add(text,'figure_text')
    for legend in fig.legends:add(legend,'legend')
    # SubFigure labels and legends are not in the top figure lists.
    for sf in getattr(fig,'subfigs',[]):
        for text in sf.texts:add(text,'figure_text')
        for legend in sf.legends:add(legend,'legend')
    return records


def _data_mask(fig,canvas,axes):
    import numpy as np
    from matplotlib.axes import Axes
    from matplotlib.figure import SubFigure
    states={}
    def hide(artist):
        if artist not in states:states[artist]=artist.get_visible()
        artist.set_visible(False)
    try:
        for parent in [fig]+list(getattr(fig,'subfigs',[])):
            for artist in parent.get_children():
                if not isinstance(artist,(Axes,SubFigure)):hide(artist)
        for ax in axes:
            data=set(ax.lines)|set(ax.collections)|set(ax.patches)|set(ax.images)
            for artist in ax.get_children():
                if artist not in data and not isinstance(artist,Axes):hide(artist)
            # Axes' background patch is not ax.patches, but explicitly hide it too.
            hide(ax.patch)
        canvas.draw()
        return np.asarray(canvas.buffer_rgba())[:,:,3].copy()>2
    finally:
        for artist,visible in states.items():artist.set_visible(visible)


def audit_layout(fig, *, mode='publication', clearance_mm=None):
    """Read rendered geometry. Findings are review risks, not certified defects.

    The mask includes visible lines, markers, bars, error bars, ribbons, meshes
    and images across axes. Bounds are conservative and include whitespace in
    a multiline label. Physical clearance uses the working canvas, which should
    be final-sized. Always inspect PNG and independently rendered PDF too.
    """
    import numpy as np
    from matplotlib.transforms import Bbox
    from matplotlib.legend import Legend
    from matplotlib.text import Annotation
    p=_profile(mode)
    gap=p['clearance_mm'] if clearance_mm is None else clearance_mm
    if isinstance(gap,bool) or not isinstance(gap,(int,float)) or not math.isfinite(gap) or gap<0:
        raise ValueError('clearance_mm must be finite and nonnegative')
    issues=[];exemptions=[];skipped=[]
    with _render_scene(fig) as (canvas,renderer):
        axes=_axes(fig);items=_items(fig,axes,renderer)
        px=fig.dpi/25.4;pad=gap*px
        frame=fig.bbox.frozen();mask=_data_mask(fig,canvas,axes)
        for i,ax in enumerate(axes):
            if ax.name!='rectilinear':skipped.append(f'axes[{i}]: {ax.name} geometry requires manual review')
            if ax.tables or any(not isinstance(a,Legend) for a in ax.artists):
                skipped.append(f'axes[{i}]: custom artists/tables need additional geometry review')
            if any(isinstance(t,Annotation) and t.get_visible() and t.arrow_patch is not None for t in ax.texts):
                skipped.append(f'axes[{i}]: annotation leader paths need manual crossing review; text boxes were checked')
        if fig.artists:skipped.append('Figure-level custom artists need additional geometry review')
        def issue(code,ids,detail,box):
            issues.append(dict(code=code,items=ids,detail=detail,box_px=list(map(float,box.extents))))
        def occupied(box):
            clipped=Bbox.intersection(box,frame)
            if clipped is None:return 0
            x0=max(0,int(math.floor(clipped.x0)));x1=min(mask.shape[1],int(math.ceil(clipped.x1)))
            y0=max(0,mask.shape[0]-int(math.ceil(clipped.y1)));y1=min(mask.shape[0],mask.shape[0]-int(math.floor(clipped.y0)))
            return int(mask[y0:y1,x0:x1].sum())
        for item in items:
            box=item['box'];artist=item['artist'];ident=item['id']
            if not frame.padded(.5).contains(box.x0,box.y0) or not frame.padded(.5).contains(box.x1,box.y1):
                issue('off_canvas',[ident],'Decoration extends beyond fixed canvas',box)
            if artist.get_clip_on() and artist.get_clip_box() is not None:
                clip=artist.get_clip_box()
                if not clip.padded(.5).contains(box.x0,box.y0) or not clip.padded(.5).contains(box.x1,box.y1):
                    issue('text_clipped',[ident],'Text box crosses its clipping rectangle',box)
            reason=getattr(artist,'_journal_overlay_reason',None)
            if reason:exemptions.append(dict(item=ident,reason=reason,scope='data overlap only'))
            elif occupied(box.padded(pad))>=3:
                issue('data_overlap' if occupied(box)>=3 else 'data_clearance',[ident],
                      'Text/legend box intersects rendered data ink or its clearance zone',box)
            for j,ax in enumerate(axes):
                own=item['owner']==f'axes[{j}]'
                if not own and item['role'] in ('axis_label','tick','offset','title'):
                    inter=Bbox.intersection(box,ax.bbox)
                    if inter is not None and inter.width>.5 and inter.height>.5:
                        issue('neighbor_axes_intrusion',[ident,f'axes[{j}]'],'Decoration enters another panel',inter)
                if ax.axison:
                    for name,spine in ax.spines.items():
                        if spine.get_visible() and spine.get_linewidth()>0:
                            path=spine.get_transform().transform_path(spine.get_path())
                            if path.intersects_bbox(box,filled=False):
                                issue('spine_crossing',[ident,f'axes[{j}].{name}'],'Text/legend box crosses an axis frame',box)
        for i,a in enumerate(items):
            for b in items[i+1:]:
                box=Bbox.intersection(a['box'].padded(pad/2),b['box'].padded(pad/2))
                if box is not None and box.width>.5 and box.height>.5:
                    actual=Bbox.intersection(a['box'],b['box'])
                    issue('decoration_overlap' if actual is not None and actual.width>.5 and actual.height>.5 else 'decoration_clearance',
                          [a['id'],b['id']],'Rendered decoration boxes touch or overlap',box)
        serial=[dict(id=a['id'],role=a['role'],text=a['text'],owner=a['owner'],box_px=list(map(float,a['box'].extents))) for a in items]
    return dict(schema_version=1,status='review' if issues or skipped else 'screen_pass',mode=mode,
                clearance_mm=gap,canvas_dpi=float(fig.dpi),size_mm=[float(v)*25.4 for v in fig.get_size_inches()],
                findings=issues,items=serial,exemptions=exemptions,skipped=skipped,
                limitations='Conservative boxes plus raster data occupancy; not glyph-level/PDF collision proof. Low-alpha/thin ink, custom artists, arrows, hidden parents and 3D need review. No automated scientific or journal certification.')


def reflow_layout(fig, *, mode='publication'):
    """Repair standard subplot decoration spacing; never resize or change fonts.

    Refuse mixed manual/Tight layouts rather than silently changing their intent.
    Use GridSpec reserved regions for outside keys/colorbars; custom arrangements
    must be repaired in their construction code.
    """
    from matplotlib.layout_engine import ConstrainedLayoutEngine
    p=_profile(mode);engine=fig.get_layout_engine();axes=_axes(fig)
    if engine is not None and not isinstance(engine,ConstrainedLayoutEngine):
        return dict(changed=False,reason='Existing non-constrained layout engine; rebuild explicitly',audit=audit_layout(fig,mode=mode))
    if any(ax.get_subplotspec() is None or not ax.get_in_layout() for ax in axes):
        return dict(changed=False,reason='Manual/inset axes need an explicit layout recipe',audit=audit_layout(fig,mode=mode))
    fig.set_layout_engine('constrained',w_pad=p['w_pad_mm']/25.4,h_pad=p['h_pad_mm']/25.4,
                          wspace=p['wspace'],hspace=p['hspace'])
    fig.align_labels();fig.canvas.draw()
    return dict(changed=True,reason='Reflowed subplot decorations at fixed canvas and font sizes',audit=audit_layout(fig,mode=mode))


def place_legend(ax, *, mode='publication', candidates=None):
    """Try a finite set of positions; restore original if none is clear.

    Operates on the current Axes legend, preserving handles/order/style/text.
    Does not create outside space: reserve a key axes and call reserved_legend
    when this returns needs_reserved_region. Explicit user-locked positions
    should be checked only, not passed to this repair helper.
    """
    legend=ax.get_legend()
    if legend is None:raise ValueError('Axes has no current legend')
    candidates=tuple(candidates or ('upper right','upper left','lower right','lower left','center right','center left','upper center','lower center','center'))
    if not 1<=len(candidates)<=12:raise ValueError('Use 1-12 finite candidate positions')
    before=audit_layout(ax.figure,mode=mode)
    with _render_scene(ax.figure) as (_,renderer):
        ident=next(x['id'] for x in _items(ax.figure,_axes(ax.figure),renderer) if x['artist'] is legend)
    if not any(ident in f['items'] for f in before['findings']):
        return dict(status='already_clear',trials=[],before=before,after=before)
    old_loc=legend._loc;old_anchor=legend._bbox_to_anchor
    trials=[];accepted=False
    try:
        legend.set_bbox_to_anchor(None)
        for loc in candidates:
            legend.set_loc(loc)
            report=audit_layout(ax.figure,mode=mode)
            hits=[f for f in report['findings'] if ident in f['items']]
            trials.append(dict(loc=loc,legend_findings=len(hits),all_findings=len(report['findings'])))
            if not hits and len(report['findings'])<=len(before['findings']):
                accepted=True
                return dict(status='placed',location=loc,trials=trials,before=before,after=report)
    finally:
        if not accepted:
            legend.set_loc(old_loc);legend._bbox_to_anchor=old_anchor
            ax.figure.canvas.draw()
    return dict(status='needs_reserved_region',trials=trials,before=before,after=audit_layout(ax.figure,mode=mode))


def reserved_legend(key_ax, handles, labels, **kwargs):
    """Place an explicit, non-deduplicated key in an already reserved GridSpec cell."""
    if key_ax.lines or key_ax.collections or key_ax.images or key_ax.patches:
        raise ValueError('Key axes contains data; reserve an empty cell')
    if len(handles)!=len(labels):raise ValueError('Handles and labels must match')
    key_ax.set_axis_off()
    return key_ax.legend(handles,labels,loc='center',**kwargs)


def place_axes_note(text, *, mode='publication', candidates=None):
    """Move a free axes-fraction note, never an annotation anchored to data."""
    from matplotlib.text import Annotation
    ax=text.axes
    if ax is None or isinstance(text,Annotation) or text.get_transform()!=ax.transAxes:
        raise ValueError('Only free notes with transform=ax.transAxes are eligible')
    candidates=tuple(candidates or ((.97,.97,'right','top'),(.03,.97,'left','top'),
                                   (.97,.03,'right','bottom'),(.03,.03,'left','bottom')))
    if not 1<=len(candidates)<=12:raise ValueError('Use 1-12 finite note candidates')
    before=audit_layout(ax.figure,mode=mode)
    with _render_scene(ax.figure) as (_,renderer):
        ident=next(x['id'] for x in _items(ax.figure,_axes(ax.figure),renderer) if x['artist'] is text)
    if not any(ident in f['items'] for f in before['findings']):
        return dict(status='already_clear',trials=[],before=before,after=before)
    original=(text.get_position(),text.get_ha(),text.get_va());accepted=False;trials=[]
    try:
        for x,y,ha,va in candidates:
            text.set_position((x,y));text.set_ha(ha);text.set_va(va)
            report=audit_layout(ax.figure,mode=mode);hits=[f for f in report['findings'] if ident in f['items']]
            trials.append(dict(position=[x,y],findings=len(hits)))
            if not hits and len(report['findings'])<=len(before['findings']):
                accepted=True
                return dict(status='placed',trials=trials,before=before,after=report)
    finally:
        if not accepted:
            text.set_position(original[0]);text.set_ha(original[1]);text.set_va(original[2])
    return dict(status='needs_reserved_region',trials=trials,before=before,after=audit_layout(ax.figure,mode=mode))


def write_audit(report,path):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False)


def save_overlay(fig, report, path):
    """Diagnostic PNG only; never modifies the delivered figure's artists."""
    from PIL import Image,ImageDraw
    import numpy as np
    path=Path(path)
    if path.exists():raise FileExistsError(path)
    with _render_scene(fig) as (canvas,_):
        canvas.draw();image=Image.fromarray(np.asarray(canvas.buffer_rgba()).copy()).convert('RGB')
    draw=ImageDraw.Draw(image)
    for f in report['findings']:
        x0,y0,x1,y1=f['box_px'];draw.rectangle((x0,image.height-y1,x1,image.height-y0),outline='#D62728',width=2)
    path.parent.mkdir(parents=True,exist_ok=True);image.save(path)
