"""Plan and apply final-size typography without changing data, colors or canvas.

All user overrides are final-placement points. A larger working canvas receives
inverse-reduction compensation. Apply again after editing: values are absolute,
so repeated calls do not accumulate scaling. No global rcParams are modified.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import math
from pathlib import Path

PRESETS = Path(__file__).resolve().parents[1]/'references/typography-presets.json'
ROLES = ('body', 'label', 'tick', 'legend', 'legend_title', 'annotation',
         'colorbar_label', 'colorbar_tick', 'panel', 'title', 'offset')
ALIASES = {'nc': 'nature-communications', 'ncomms': 'nature-communications',
           'nature communications': 'nature-communications',
           'physical review letters': 'prl', 'physical review e': 'pre',
           'the journal of chemical physics': 'jcp',
           'the journal of physical chemistry letters': 'jpcl'}


def positive(value, name):
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or value <= 0:
        raise ValueError(f'{name} must be finite and positive')
    return float(value)


def tag_text(artist, role):
    """Mark a Text artist's semantic role (panel, annotation, title, etc.)."""
    if role not in ROLES:
        raise ValueError(f'Unknown typography role: {role}')
    artist._journal_font_role = role
    return artist


@dataclass
class FontPlan:
    journal: str
    profile: dict
    final_width_mm: float
    canvas_width_mm: float
    final_pt: dict

    @property
    def reduction(self):
        return self.final_width_mm / self.canvas_width_mm

    def pt(self, role):
        """Working-canvas points for a role."""
        return self.final_pt[role] / self.reduction

    def rc(self):
        return {
            'font.size': self.pt('body'), 'axes.labelsize': self.pt('label'),
            'axes.titlesize': self.pt('title'), 'figure.titlesize': self.pt('title'),
            'figure.labelsize': self.pt('label'), 'xtick.labelsize': self.pt('tick'),
            'ytick.labelsize': self.pt('tick'), 'legend.fontsize': self.pt('legend'),
            'legend.title_fontsize': self.pt('legend_title'),
        }

    def warnings(self):
        warnings = []
        low, high = self.profile['body_range_pt']
        for role, pt in self.final_pt.items():
            if role == 'panel':
                continue
            if low is not None and pt < low - 1e-6:
                warnings.append(f'{role}={pt:g} pt is below the recorded {low:g} pt bound; see source status')
            if high is not None and pt > high + 1e-6:
                warnings.append(f'{role}={pt:g} pt exceeds the recorded {high:g} pt bound; see source status')
        panel = self.final_pt['panel']
        required = self.profile.get('panel_required_pt')
        if required is not None and abs(panel-required) > 1e-6:
            warnings.append(f'panel={panel:g} pt differs from required {required:g} pt')
        if required is None and low is not None and panel < low:
            warnings.append(f'panel={panel:g} pt is below the recorded {low:g} pt bound')
        if required is None and high is not None and panel > high:
            # NC has only a dated optimal range, no verified separate panel exception.
            warnings.append(f'panel={panel:g} pt exceeds the recorded {high:g} pt body range; panel size is a local choice')
        if self.profile.get('glyph_min_mm'):
            warnings.append('APS: measure representative rendered glyphs at final size; nominal points do not certify 2 mm lettering height')
        if self.journal in ('nature-communications', 'pnas', 'science'):
            warnings.append(self.profile['status'])
        if abs(self.reduction - 1) > 1e-6:
            warnings.append('Compensated working canvas: line widths, markers and gaps also scale on placement; audit them separately or rebuild at final size')
        return warnings

    def to_dict(self):
        return dict(schema_version=1, journal=self.journal,
                    final_width_mm=self.final_width_mm, canvas_width_mm=self.canvas_width_mm,
                    reduction=self.reduction, final_pt=self.final_pt,
                    canvas_pt={r:self.pt(r) for r in ROLES},
                    source_status=self.profile['status'], sources=self.profile['sources'],
                    checked=json.loads(PRESETS.read_text(encoding='utf-8'))['checked'],
                    warnings=self.warnings())

    def apply(self, fig, *, colorbars=()):
        """Apply to existing visible text, including colorbars and figure legends.

        Pass Colorbar objects explicitly (custom colorbar axes also accepted).
        Untagged free text is an annotation; tag panel letters rather than guessing
        from their content. Shared/twin/inset axes are included through fig.axes.
        Changes font sizes only; panel weight/style uses the selected convention.
        """
        from matplotlib.text import Text
        if abs(fig.get_figwidth()*25.4-self.canvas_width_mm) > 1e-4:
            raise ValueError('Figure canvas width differs from FontPlan; resolve a new plan')
        fig.canvas.draw()  # Materialize lazy ticks/offset labels before mapping.
        mapped = {}
        def assign(artist, role):
            if artist is not None: mapped[artist] = role
        cb_axes = {getattr(c, 'ax', c) for c in colorbars}
        legends = list(fig.legends)
        for ax in fig.axes:
            is_cb = ax in cb_axes or getattr(ax, '_colorbar', None) is not None
            for axis in [ax.xaxis, ax.yaxis] + ([ax.zaxis] if hasattr(ax, 'zaxis') else []):
                assign(axis.label, 'colorbar_label' if is_cb else 'label')
                assign(axis.get_offset_text(), 'offset')
                role = 'colorbar_tick' if is_cb else 'tick'
                ax.tick_params(axis='both', which='both', labelsize=self.pt(role))
                for tick in axis.get_major_ticks() + axis.get_minor_ticks():
                    assign(tick.label1, role); assign(tick.label2, role)
            for title in (ax.title, ax._left_title, ax._right_title): assign(title, 'title')
            if ax.get_legend() is not None: legends.append(ax.get_legend())
        # Also include multiple manually-added legends.
        from matplotlib.legend import Legend
        legends += fig.findobj(match=Legend)
        for legend in set(legends):
            for text in legend.get_texts(): assign(text, 'legend')
            assign(legend.get_title(), 'legend_title')
        assign(getattr(fig, '_suptitle', None), 'title')
        assign(getattr(fig, '_supxlabel', None), 'label')
        assign(getattr(fig, '_supylabel', None), 'label')
        records=[]
        for artist in fig.findobj(match=Text):
            role = getattr(artist, '_journal_font_role', mapped.get(artist, 'annotation'))
            artist.set_fontsize(self.pt(role))
            if role == 'panel':
                artist.set_fontweight(self.profile['panel_weight']); artist.set_fontstyle('normal')
            if artist.get_visible() and artist.get_text().strip():
                records.append(dict(text=artist.get_text(), role=role,
                                    canvas_pt=artist.get_fontsize(),
                                    effective_final_pt=artist.get_fontsize()*self.reduction))
        fig.canvas.draw()
        return dict(plan=self.to_dict(), texts=records,
                    limitation='Text roles and nominal sizes only; math subscripts, glyph ink height, overlaps and actual manuscript placement need review')


def resolve_typography(journal, *, final_width_mm, canvas_width_mm=None,
                       font_scale=1.0, body_pt=None, overrides=None):
    """Resolve defaults -> body-relative scale -> font_scale -> absolute overrides.

    Defaults are local design choices. Overrides are never silently clamped;
    warnings retain conflicts with dated publisher guidance.
    """
    key = journal.strip().lower()
    key = ALIASES.get(key, key)
    profiles = json.loads(PRESETS.read_text(encoding='utf-8'))['profiles']
    if key not in profiles: raise ValueError(f'Unknown journal {journal!r}; choose {list(profiles)}')
    profile = profiles[key]
    final_width_mm = positive(final_width_mm, 'final_width_mm')
    canvas_width_mm = final_width_mm if canvas_width_mm is None else positive(canvas_width_mm, 'canvas_width_mm')
    factor = positive(font_scale, 'font_scale')
    if body_pt is not None: factor *= positive(body_pt, 'body_pt') / profile['body_pt']
    sizes = {r:profile['body_pt'] for r in ROLES}
    for r in ('tick','legend','annotation','colorbar_tick','offset'): sizes[r] = profile['tick_pt']
    sizes['panel'] = profile['panel_pt']
    sizes = {r:float(pt)*factor for r,pt in sizes.items()}
    for role,value in (overrides or {}).items():
        if role not in ROLES: raise ValueError(f'Unknown role {role!r}; choose {ROLES}')
        sizes[role] = positive(value, role)
    return FontPlan(key, profile, final_width_mm, canvas_width_mm, sizes)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--journal', required=True)
    p.add_argument('--final-width-mm', required=True, type=float)
    p.add_argument('--canvas-width-mm', type=float)
    p.add_argument('--font-scale', default=1, type=float)
    p.add_argument('--body-pt', type=float)
    p.add_argument('--set', action='append', default=[], metavar='ROLE=PT')
    p.add_argument('--output', type=Path)
    a=p.parse_args()
    try:
        overrides={}
        for entry in a.set:
            role,value=entry.split('=',1); overrides[role]=float(value)
        plan=resolve_typography(a.journal,final_width_mm=a.final_width_mm,
                               canvas_width_mm=a.canvas_width_mm,font_scale=a.font_scale,
                               body_pt=a.body_pt,overrides=overrides)
        text=json.dumps(plan.to_dict(),ensure_ascii=False,indent=2,allow_nan=False)
        if a.output:
            a.output.parent.mkdir(parents=True,exist_ok=True)
            with a.output.open('x',encoding='utf-8') as f: f.write(text+'\n')
        print(text)
    except (ValueError, OSError) as e: p.error(str(e))


if __name__ == '__main__': main()
