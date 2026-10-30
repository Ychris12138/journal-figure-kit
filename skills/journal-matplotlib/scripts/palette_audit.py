"""Screen proposed color cards. This never approves or modifies a palette."""
from __future__ import annotations
import argparse
from itertools import combinations
import math
from pathlib import Path
from palette_cards import load_deck, write_json


def rgb(value):
    return tuple(int(value[i:i+2], 16) / 255 for i in (1, 3, 5))


def luminance(value):
    linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055)**2.4 for v in value]
    return sum(a*b for a, b in zip(linear, (.2126, .7152, .0722)))


def gray(value):
    y = luminance(value)
    encoded = 12.92*y if y <= .0031308 else 1.055*y**(1/2.4)-.055
    return [encoded]*3


def contrast(a, b):
    lo, hi = sorted((luminance(a), luminance(b)))
    return (hi+.05)/(lo+.05)


def lightness(value):
    y = luminance(value)
    return 116*y**(1/3)-16 if y > (6/29)**3 else (29/3)**3*y


def audit_card(card):
    labels = list(card['mapping']) if card['kind'] == 'categorical' else [f'Anchor {i+1}' for i in range(len(card['colors']))]
    values = list(card['mapping'].values()) if card['kind'] == 'categorical' else card['colors']
    bg = rgb(card['background'])
    colors = [rgb(value) for value in values]
    bands = [[card['band_alpha']*v+(1-card['band_alpha'])*b for v, b in zip(c, bg)] for c in colors]
    close = []
    for i, j in combinations(range(len(colors)), 2):
        difference = abs(lightness(colors[i])-lightness(colors[j]))
        if difference < 5:
            close.append({'pair': [labels[i], labels[j]], 'delta_Lstar': round(difference, 3)})
    return {
        'id': card['id'], 'kind': card['kind'], 'colors': values, 'labels': labels,
        'text_background_contrast': contrast(rgb(card['text']), bg),
        'mark_background_contrast': [contrast(c, bg) for c in colors],
        'band_background_contrast': [contrast(c, bg) for c in bands],
        'close_grayscale_pairs': close,
        'scope': 'Categorical entries or continuous anchors only; not a full colormap monotonicity test.',
    }


def simulate(values, kind):
    import numpy as np
    from colorspacious import cspace_convert
    converted = cspace_convert(np.asarray(values),
                              {'name': 'sRGB1+CVD', 'cvd_type': kind, 'severity': 100}, 'sRGB1')
    if not np.isfinite(converted).all():
        raise ValueError('CVD conversion returned nonfinite values')
    count = int(np.any((converted < 0) | (converted > 1), axis=1).sum())
    return np.clip(converted, 0, 1).tolist(), count


def audit(deck, output, *, cvd=True):
    import matplotlib as mpl
    mpl.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    report = {
        'schema_version': 1, 'status': 'review_only', 'palette_approval': 'pending_or_external',
        'method': 'sRGB relative luminance, luminance-preserving grayscale; CIE L* pair difference < 5 is a local heuristic.',
        'cvd_method': 'colorspacious / Machado et al. 2009, severity 100; screen simulation, not diagnosis or certification.',
        'limitations': 'Contrast values are measurements, not universal print thresholds. Preview original marks, overlaps and bands at final size. Continuous anchors do not certify a colormap.',
        'cards': [audit_card(card) for card in deck['cards']], 'skipped': [],
    }
    kinds = [('Original', None), ('Grayscale', 'gray')]
    if cvd:
        try:
            import colorspacious
        except ImportError:
            report['skipped'].append('CVD: colorspacious unavailable; install explicitly to enable it')
        else:
            report['colorspacious_version'] = getattr(colorspacious, '__version__', 'unknown')
            kinds += [('Deutan 100', 'deuteranomaly'), ('Protan 100', 'protanomaly'), ('Tritan 100', 'tritanomaly')]
    else:
        report['skipped'].append('CVD disabled by caller')
    with mpl.rc_context({'font.family': 'DejaVu Sans', 'font.size': 8, 'pdf.fonttype': 42, 'savefig.bbox': None}):
        fig, axes = plt.subplots(len(deck['cards']), len(kinds), squeeze=False,
                                 figsize=(2.2*len(kinds), 1.85*len(deck['cards'])+.45), layout='constrained')
        for row, card in enumerate(deck['cards']):
            item = report['cards'][row]
            base = [rgb(v) for v in item['colors']]
            item['cvd_gamut_clipped_colors'] = {}
            for col, (label, kind) in enumerate(kinds):
                all_colors = base + [rgb(card['background']), rgb(card['text'])]
                if kind == 'gray':
                    converted = [gray(c) for c in all_colors]
                elif kind:
                    converted, clipped = simulate(all_colors, kind)
                    item['cvd_gamut_clipped_colors'][kind] = clipped
                else:
                    converted = all_colors
                ax = axes[row, col]
                ax.set_facecolor(converted[-2])
                ax.set(xlim=(0, len(base)), ylim=(0, 1), yticks=[], xticks=[])
                for index, c in enumerate(converted[:-2]):
                    ax.add_patch(Rectangle((index+.07, .53), .86, .34, facecolor=c))
                    ax.plot([index+.07, index+.93], [.3, .3], color=c, lw=1.2,
                            ls=['-', '--', '-.', ':'][index%4], marker=['o', 's', '^', 'D'][index%4], ms=3)
                    ax.text(index+.5, .06, str(index+1), ha='center', color=converted[-1])
                ax.set_title(f"{card['id']} | {label}")
                for spine in ax.spines.values():
                    spine.set_linewidth(.4)
        fig.suptitle('Palette screening | synthetic marks | no approval or accessibility certification', fontsize=10)
        fig.savefig(output/'palette-audit.png', dpi=180)
        fig.savefig(output/'palette-audit.pdf')
        plt.close(fig)
    write_json(output/'palette-audit.json', report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--deck', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--no-cvd', action='store_true')
    args = parser.parse_args()
    report = audit(load_deck(args.deck), args.output, cvd=not args.no_cvd)
    print(f"Screened {len(report['cards'])} cards; {len(report['skipped'])} skipped checks. Human review required.")
    return 1 if report['skipped'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
