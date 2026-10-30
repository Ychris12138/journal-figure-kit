"""Reproducible synthetic QA gallery. Colors here are test fixtures, not approval."""
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'skills/journal-matplotlib/scripts'))
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
import numpy as np
from figure_export import export_pair

RC = {'font.family': 'DejaVu Sans', 'font.size': 7, 'axes.labelsize': 7,
      'axes.linewidth': .65, 'axes.spines.top': False, 'axes.spines.right': False,
      'xtick.labelsize': 7, 'ytick.labelsize': 7, 'legend.fontsize': 6.5,
      'legend.frameon': False, 'savefig.bbox': None, 'pdf.fonttype': 42}
COLORS = {'component_A': '#022DFE', 'component_B': '#FE9301', 'total': '#010101'}
NORM = TwoSlopeNorm(vmin=-1, vcenter=0, vmax=2)


def profile(ax, label=None):
    x = np.linspace(-3, 3, 121)
    a = np.exp(-((x+.5)/.9)**2)
    b = .7*np.exp(-((x-.7)/1.1)**2)
    for key, y, style, marker in [('component_A', a, '--', 's'), ('component_B', b, '-.', '^'), ('total', a+b, '-', 'o')]:
        ax.plot(x, y, color=COLORS[key], ls=style, marker=marker, markevery=24, ms=2.6,
                lw=1, label=key.replace('_', ' '))
    ax.set(xlabel=r'$z$ (nm)', ylabel=r'$\rho$ (arbitrary units)', xlim=(-3, 3), ylim=(0, 1.65))
    if label:
        ax.text(.02, .97, label, weight='bold', va='top', transform=ax.transAxes, fontsize=8)
    return ax.get_legend_handles_labels()


def field(fig, ax, label=None):
    x = np.linspace(-2, 2, 101); y = np.linspace(-1, 1, 51)
    xx, yy = np.meshgrid(x, y)
    z = 2*np.exp(-((xx-.7)**2+yy**2)) - np.exp(-((xx+1.1)**2+2*yy**2))
    im = ax.imshow(z, extent=(-2, 2, -1, 1), origin='lower', cmap='RdBu_r', norm=NORM, aspect='equal')
    ax.set(xlabel='x (nm)', ylabel='y (nm)')
    # Follow the displayed image height, not its larger GridSpec allocation.
    cax = ax.inset_axes([1.04, 0, .045, 1])
    fig.colorbar(im, cax=cax, label=r'$\Delta q$ (a.u.)', ticks=[-1, 0, 1, 2])
    if label:
        ax.text(.02, .97, label, weight='bold', va='top', transform=ax.transAxes, fontsize=8)


def build(output):
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    manifest = []
    def save(fig, name, width, height):
        report = export_pair(fig, output/name, width_mm=width, height_mm=height,
                             provenance={'data': 'deterministic synthetic functions in examples/gallery.py',
                                         'palette_approval': 'synthetic fixture only; no real-data authorization',
                                         'mapping': COLORS, 'numeric_norm': {'vmin': -1, 'center': 0, 'vmax': 2},
                                         'uncertainty': 'none; no measured samples or inferred CI'})
        manifest.append({'stem': name, 'size_mm': [width, height], 'layout_warnings': report['layout_warnings']})
        plt.close(fig)
    with mpl.rc_context(RC):
        fig = plt.figure(figsize=(180/25.4, 52/25.4), layout='constrained')
        grid = fig.add_gridspec(1, 3, width_ratios=[1, .42, 1.04])
        ax = fig.add_subplot(grid[0]); handles, labels = profile(ax, 'a')
        legend_ax = fig.add_subplot(grid[1]); legend_ax.axis('off')
        legend_ax.legend(handles, labels, loc='center', handlelength=2.3)
        field(fig, fig.add_subplot(grid[2]), 'b')
        save(fig, 'overview', 180, 52)
        fig, ax = plt.subplots(figsize=(89/25.4, 65/25.4), layout='constrained')
        profile(ax); ax.legend(loc='upper right')
        save(fig, 'overview/panel-a', 89, 65)
        fig, ax = plt.subplots(figsize=(89/25.4, 40/25.4), layout='constrained')
        field(fig, ax)
        save(fig, 'overview/panel-b', 89, 40)
        fig, ax = plt.subplots(figsize=(89/25.4, 65/25.4), layout='constrained')
        x = np.linspace(0, 10, 41); y = np.exp(-x/3); y[16:22] = np.nan
        ax.plot(x, y, color='#333333', marker='o', markevery=4, ms=3)
        ax.set(xlabel=r'$t$ (ps)', ylabel=r'$C_{\alpha}(t)$', xlim=(0, 10), ylim=(0, 1.1))
        ax.text(.51, .8, 'Missing observations', transform=ax.transAxes, ha='center', fontsize=6.5)
        save(fig, 'missing-gap', 89, 65)
    (output/'gallery.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='build/gallery')
    args = parser.parse_args()
    build(args.output)
    print(args.output)
