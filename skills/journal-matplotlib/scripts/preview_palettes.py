#!/usr/bin/env python3
"""Render palette candidates using synthetic data, before real-data color approval."""
import argparse
import json
from pathlib import Path
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--ids', nargs='+', default=['okabe_ito', 'tol_bright', 'tol_high_contrast', 'tol_muted', 'cividis', 'viridis', 'RdBu_r'])
    parser.add_argument('--dpi', type=int, default=180)
    args = parser.parse_args()
    presets = json.loads((Path(__file__).resolve().parents[1] / 'references/palettes.json').read_text(encoding='utf-8'))
    all_ids = set(presets['categorical']) | set(presets['continuous'])
    if any(name not in all_ids for name in args.ids):
        parser.error('Unknown palette; select IDs from references/palettes.json')
    if args.dpi <= 0:
        parser.error('dpi must be positive')
    args.output.mkdir(parents=True, exist_ok=True)
    rc = {'font.family': 'DejaVu Sans', 'font.size': 8, 'pdf.fonttype': 42,
          'axes.spines.top': False, 'axes.spines.right': False,
          'savefig.bbox': None, 'axes.linewidth': .6}
    with mpl.rc_context(rc):
        fig = plt.figure(figsize=(8.4, 1.12 * len(args.ids) + .6), layout='constrained')
        grid = fig.add_gridspec(len(args.ids), 2, width_ratios=[1.45, 1])
        for row, name in enumerate(args.ids):
            left, right = fig.add_subplot(grid[row, 0]), fig.add_subplot(grid[row, 1])
            left.set_axis_off()
            left.set_xlim(0, 1); left.set_ylim(0, 1)
            if name in presets['categorical']:
                item = presets['categorical'][name]
                colors = item['colors']
                left.text(0, .95, item['label'], weight='bold', va='top', fontsize=10)
                for index, color in enumerate(colors):
                    x = index / len(colors)
                    left.add_patch(Rectangle((x, .38), .90 / len(colors), .25, facecolor=color))
                    left.text(x, .29, color, fontsize=5.9, va='top', rotation=0)
                left.text(0, .04, f'{len(colors)} categories | exact source colors', fontsize=7, color='#444444')
                x = np.linspace(0, 1, 60)
                styles = ['-', '--', '-.', ':']
                markers = ['o', 's', '^', 'D']
                for index, color in enumerate(colors[:4]):
                    y = np.exp(-(index + 1) * x) + .12 * index
                    right.plot(x, y, color=color, lw=1.3, ls=styles[index], marker=markers[index],
                               markevery=12, ms=3, label=f'Group {index + 1}')
                right.set(xlim=(0, 1), ylim=(0, 1.55), xlabel='Synthetic x', ylabel='Synthetic y')
                right.tick_params(labelsize=7)
            else:
                item = presets['continuous'][name]
                left.text(0, .95, f'{name} / {item["kind"]}', weight='bold', va='top', fontsize=10)
                grad = np.linspace(0, 1, 256)[None, :]
                left.imshow(grad, extent=(0, .97, .35, .65), aspect='auto', cmap=name)
                left.text(0, .25, 'Confirm map, units, limits and normalization', fontsize=7)
                x = np.linspace(-2, 2, 70)
                xx, yy = np.meshgrid(x, x)
                if item['kind'] == 'diverging':
                    z = np.sin(xx) * np.cos(yy)
                    limits = {'vmin': -1, 'vmax': 1}
                elif item['kind'] == 'cyclic':
                    z = np.arctan2(yy, xx)
                    limits = {'vmin': -np.pi, 'vmax': np.pi}
                else:
                    z = np.exp(-xx**2 - yy**2)
                    limits = {'vmin': 0, 'vmax': 1}
                im = right.imshow(z, cmap=name, origin='lower', aspect='auto', extent=(-2, 2, -2, 2), **limits)
                right.set(xlabel='Synthetic x', ylabel='Synthetic y')
                fig.colorbar(im, ax=right, label='Demo value', fraction=.045, pad=.025)
        fig.suptitle('Palette candidates | synthetic examples only', fontsize=12, weight='bold')
        fig.savefig(args.output / 'palette-candidates.png', dpi=args.dpi, facecolor='white')
        fig.savefig(args.output / 'palette-candidates.pdf', dpi=300, facecolor='white')
        plt.close(fig)
    print(args.output / 'palette-candidates.png')


if __name__ == '__main__':
    main()
