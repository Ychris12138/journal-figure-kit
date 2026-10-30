#!/usr/bin/env python3
"""Preview color cards; record a human choice; export only its matching settings."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import textwrap


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')


def color(value):
    if not isinstance(value, str) or not re.fullmatch(r'#[0-9A-Fa-f]{6}', value):
        raise ValueError(f'Expected six-digit HEX color, got {value!r}')


def validate_card(card):
    for key in ('id', 'title', 'changes', 'use', 'caveat'):
        if not isinstance(card.get(key), str) or not card[key].strip():
            raise ValueError(f'Card requires nonempty {key}')
    if type(card.get('revision')) is not int or card['revision'] < 1:
        raise ValueError('revision must be a positive integer')
    source = card.get('source')
    if not isinstance(source, dict) or not source.get('type') or not any(source.get(k) for k in ('url', 'path', 'attachment_id')):
        raise ValueError('source requires type and URL, local path, or attachment ID')
    for key in ('background', 'text', 'reference'):
        color(card.get(key))
    alpha = card.get('band_alpha')
    if type(alpha) not in (float, int) or not math.isfinite(alpha) or not 0 <= alpha <= 1:
        raise ValueError('band_alpha must be a finite value in [0, 1]')
    for value in card.get('observed_colors', []):
        color(value)
    kind = card.get('kind')
    if kind == 'categorical':
        mapping = card.get('mapping')
        if not isinstance(mapping, dict) or not mapping or any(not isinstance(k, str) or not k.strip() for k in mapping):
            raise ValueError('categorical card requires nonempty labeled mapping')
        for value in mapping.values():
            color(value)
        if len(set(v.upper() for v in mapping.values())) != len(mapping):
            raise ValueError('Repeated category colors: propose distinguishable colors or facets')
    elif kind in ('sequential', 'diverging', 'cyclic'):
        anchors = card.get('colors')
        if not isinstance(anchors, list) or len(anchors) < 2:
            raise ValueError('continuous card requires at least two color anchors')
        for value in anchors:
            color(value)
        norm = card.get('normalization', {})
        for key in ('vmin', 'vmax'):
            if type(norm.get(key)) not in (int, float) or not math.isfinite(norm[key]):
                raise ValueError(f'normalization requires finite {key}')
        if norm['vmin'] >= norm['vmax']:
            raise ValueError('normalization requires vmin < vmax')
        if norm.get('scale') not in ('linear', 'log'):
            raise ValueError('scale must be linear or log')
        if norm['scale'] == 'log' and norm['vmin'] <= 0:
            raise ValueError('log normalization requires positive vmin')
        if not isinstance(norm.get('units'), str) or not norm['units'].strip():
            raise ValueError('Declare units, including dimensionless when appropriate')
        color(norm.get('missing_color'))
        if kind == 'diverging':
            center = norm.get('center')
            if type(center) not in (int, float) or not norm['vmin'] < center < norm['vmax'] or norm['scale'] != 'linear':
                raise ValueError('diverging card requires interior center and linear scale')
        if kind == 'cyclic' and (anchors[0].upper() != anchors[-1].upper() or norm['scale'] != 'linear'):
            raise ValueError('cyclic map must join endpoints over a linear periodic range')
    else:
        raise ValueError('Unknown kind')
    return card


def load_deck(path):
    deck = read_json(path)
    if not isinstance(deck, dict) or deck.get('schema_version') != 1 or not isinstance(deck.get('cards'), list) or not deck['cards']:
        raise ValueError('Expected schema_version 1 and nonempty cards')
    ids = []
    for card in deck['cards']:
        validate_card(card)
        ids.append(card['id'])
    if len(set(ids)) != len(ids):
        raise ValueError('Card IDs must be unique within a deck')
    return deck


def fingerprint(card):
    # JSON object key order is irrelevant except category order, which affects encoding.
    payload = dict(card)
    if 'mapping' in card:
        payload['mapping'] = list(card['mapping'].items())
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def select(deck, card_id):
    found = [c for c in deck['cards'] if c['id'] == card_id]
    if len(found) != 1:
        raise ValueError(f'Card {card_id!r} not found')
    return found[0]


def confirm(deck, card_id, reply, scope):
    # The caller must verify this is a real human reply, not a model-generated quote.
    if not reply.strip() or not scope.strip():
        raise ValueError('Confirmation requires the real user reply and an explicit scope')
    card = select(deck, card_id)
    return {'schema_version': 1, 'status': 'confirmed', 'card': card,
            'fingerprint': fingerprint(card), 'user_reply': reply, 'scope': scope,
            'confirmed_at': datetime.now(timezone.utc).isoformat()}


def approved_settings(deck, approval):
    if approval.get('status') != 'confirmed':
        raise ValueError('Palette is pending; obtain user confirmation before applying it')
    if not approval.get('user_reply', '').strip() or not approval.get('scope', '').strip() or not approval.get('confirmed_at'):
        raise ValueError('Missing confirmation evidence')
    card = validate_card(approval['card'])
    digest = fingerprint(card)
    if digest != approval.get('fingerprint') or digest != fingerprint(select(deck, card['id'])):
        raise ValueError('Card changed since confirmation; preview and confirm the revised card')
    return {**card, 'fingerprint': digest, 'confirmation': {
        k: approval[k] for k in ('status', 'user_reply', 'scope', 'confirmed_at')}}


def preview(deck, output, dpi=200, font=None):
    import numpy as np
    import matplotlib as mpl
    mpl.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    from matplotlib.patches import Rectangle
    from matplotlib.colors import LinearSegmentedColormap, Normalize, LogNorm, TwoSlopeNorm
    if font:
        font_manager.fontManager.addfont(str(font))
        family = font_manager.FontProperties(fname=str(font)).get_name()
    else:
        available = {f.name for f in font_manager.fontManager.ttflist}
        family = next((f for f in ('Microsoft YaHei', 'Noto Sans CJK SC', 'SimHei') if f in available), 'DejaVu Sans')
    if dpi <= 0:
        raise ValueError('dpi must be positive')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    rc = {'font.family': family, 'font.size': 8, 'pdf.fonttype': 42, 'ps.fonttype': 42,
          'axes.spines.top': False, 'axes.spines.right': False, 'axes.linewidth': .65,
          'savefig.bbox': None, 'axes.unicode_minus': False}
    with mpl.rc_context(rc):
        fig = plt.figure(figsize=(12.4, 3.12 * len(deck['cards']) + .7), layout='constrained')
        grid = fig.add_gridspec(len(deck['cards']), 3, width_ratios=[1.7, 1.05, .85])
        for row, card in enumerate(deck['cards']):
            left, plot, detail = [fig.add_subplot(grid[row, col]) for col in range(3)]
            left.set_axis_off();left.set_xlim(0, 1);left.set_ylim(0, 1)
            left.text(0, .99, f"{card['id']}  r{card['revision']} · {card['title']}", va='top', weight='bold', fontsize=11)
            source=card['source']
            locator=source.get('figure',source.get('region',''))
            origin=source.get('url',source.get('path',source.get('attachment_id','')))
            if origin.startswith('https://doi.org/'):origin=origin[len('https://doi.org/'):]
            elif source.get('path'):origin=Path(origin).name
            left.text(0,.928,textwrap.shorten(f'{locator} · {origin}',width=76,placeholder='...'),fontsize=6.1,va='top',color='#555555')
            observed = card.get('observed_colors', [])
            if observed:
                left.text(0, .88, '来源取样 / Source samples', va='top', fontsize=7, color='#555555')
                for i, value in enumerate(observed):
                    left.add_patch(Rectangle((.49+i*.48/len(observed), .833), .44/len(observed), .048, facecolor=value))
            values = list(card['mapping'].values()) if card['kind'] == 'categorical' else card['colors']
            labels = list(card['mapping']) if card['kind'] == 'categorical' else [f'Anchor {i+1}' for i in range(len(values))]
            left.text(0, .78, '建议配色与映射 / Proposed colors', fontsize=7, va='top')
            for i, value in enumerate(values):
                xx = i / len(values)
                left.add_patch(Rectangle((xx, .615), .9 / len(values), .105, facecolor=value, edgecolor='#D0D0D0', lw=.4))
                left.text(xx, .585, value, fontsize=6.8, va='top')
                left.text(xx, .531, labels[i], fontsize=6.8, va='top', wrap=True)
            desc = [f"用途：{card['use']}", f"调整：{card['changes']}", f"检查：{card['caveat']}"]
            for yy, text in zip((.42, .29, .12), desc):
                # Wrap CJK at an explicit width; English provenance stays on the source line.
                chunks = [text[i:i+36] for i in range(0, len(text), 36)]
                left.text(0, yy, '\n'.join(chunks), fontsize=7.1, va='top', linespacing=1.2)
            left.text(0,.018,f"背景 {card['background']} · 文字 {card['text']} · 参照 {card['reference']} · band alpha={card['band_alpha']}",fontsize=6.1,va='top',color='#555555')
            for ax in (plot, detail):
                ax.set_facecolor(card['background'])
                # Labels outside the axes sit on the neutral white comparison sheet.
                ax.tick_params(colors='#222222', labelsize=7)
                for spine in ax.spines.values():spine.set_color(card['text'])
                ax.xaxis.label.set_color('#222222');ax.yaxis.label.set_color('#222222')
            if card['kind'] == 'categorical':
                x = np.linspace(0, 1, 100)
                for i, value in enumerate(values):
                    y = np.exp(-(i+1)*x) + .13*i
                    plot.fill_between(x, y-.055, y+.055, color=value, alpha=card['band_alpha'], linewidth=0)
                    plot.plot(x, y, color=value, ls=['-', '--', '-.', ':'][i%4], marker=['o', 's', '^', 'D', 'v'][i%5], markevery=22, ms=3, lw=1.25)
                plot.axhline(.15, color=card['reference'], ls=':', lw=.8)
                plot.set(xlabel='Synthetic x', ylabel='Synthetic response', xlim=(0,1), ylim=(0,max(1.5,.13*len(values)+.5)))
                heights = np.linspace(.65, 1.05, len(values))
                detail.bar(np.arange(len(values)), heights, color=values)
                # A contrasting halo keeps black-on-black uncertainty visible
                # without changing the proposed data colors or error magnitudes.
                from matplotlib import patheffects
                errors = detail.errorbar(np.arange(len(values)), heights, yerr=.07,
                                        fmt='none', capsize=2, color=card['text'], elinewidth=.8)
                for artist in (*errors.lines[1], *errors.lines[2]):
                    artist.set_path_effects([patheffects.withStroke(linewidth=2.2, foreground=card['background'])])
                detail.set_xticks(np.arange(len(values)), [f'G{i+1}' for i in range(len(values))])
                detail.set(xlabel='Same groups', ylabel='Synthetic mean', ylim=(0,1.3))
                plot.set_title('曲线 + 同色误差带', fontsize=9)
                detail.set_title('面填充 + 误差棒', fontsize=9)
            else:
                cfg = card['normalization'];lo, hi = cfg['vmin'], cfg['vmax']
                cmap = LinearSegmentedColormap.from_list(card['id'], values)
                cmap.set_bad(cfg['missing_color'])
                t = np.linspace(-2,2,80);xx,yy = np.meshgrid(t,t)
                base = (np.sin(xx)*np.cos(yy)+1)/2
                if card['kind'] == 'diverging':
                    center=cfg['center'];signed=2*base-1
                    z = np.where(signed>=0,center+signed*(hi-center),center+signed*(center-lo))
                    norm = TwoSlopeNorm(vmin=lo,vcenter=center,vmax=hi)
                elif cfg['scale'] == 'log':
                    z=np.exp(np.log(lo)+base*(np.log(hi)-np.log(lo)));norm=LogNorm(lo,hi)
                else:
                    z=lo+base*(hi-lo);norm=Normalize(lo,hi)
                if card['kind']=='cyclic':z=lo+(np.arctan2(yy,xx)+np.pi)/(2*np.pi)*(hi-lo)
                im=plot.imshow(z,cmap=cmap,norm=norm,origin='lower',extent=(-2,2,-2,2),aspect='auto')
                fig.colorbar(im,ax=plot,label=cfg['units'],fraction=.045,pad=.035)
                detail.imshow(np.linspace(lo,hi,256)[None,:],cmap=cmap,norm=norm,aspect='auto',extent=(lo,hi,0,1))
                detail.set_yticks([]);detail.set_xlabel(cfg['units'])
                plot.set_title('合成连续场 / Synthetic field',fontsize=9)
                detail.set_title('归一化与范围见色卡记录',fontsize=9)
        fig.suptitle(deck.get('title','Palette cards')+' · 合成示例，等待确认 / Pending approval',fontsize=13,weight='bold')
        fig.savefig(output/'palette-cards.png',dpi=dpi,facecolor='white')
        fig.savefig(output/'palette-cards.pdf',dpi=300,facecolor='white')
        plt.close(fig)
    write_json(output/'palette-proposal.json', {'schema_version':1,'status':'pending','deck':deck,
               'fingerprints':{c['id']:fingerprint(c) for c in deck['cards']}})


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command',required=True)
    p=commands.add_parser('preview');p.add_argument('--deck',required=True);p.add_argument('--output',required=True)
    p.add_argument('--dpi',type=int,default=200);p.add_argument('--font',type=Path)
    p=commands.add_parser('confirm');p.add_argument('--deck',required=True);p.add_argument('--id',required=True)
    p.add_argument('--reply',required=True);p.add_argument('--scope',required=True);p.add_argument('--output',required=True)
    p=commands.add_parser('export');p.add_argument('--deck',required=True);p.add_argument('--approval',required=True);p.add_argument('--output',required=True)
    args=parser.parse_args(argv)
    try:
        deck=load_deck(args.deck)
        if args.command=='preview':preview(deck,args.output,args.dpi,args.font)
        elif args.command=='confirm':write_json(args.output,confirm(deck,args.id,args.reply,args.scope))
        else:write_json(args.output,approved_settings(deck,read_json(args.approval)))
    except (ValueError,KeyError,OSError,ImportError) as error:
        parser.error(str(error))
    print(args.output)
    return 0


if __name__=='__main__':
    raise SystemExit(main())
