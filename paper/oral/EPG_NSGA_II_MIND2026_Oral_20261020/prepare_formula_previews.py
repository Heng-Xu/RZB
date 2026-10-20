"""Render exact mathematical expressions as portable SVG path fragments.

Only preview fragments are written. Slide sources retain their exact LaTeX
markers and export to editable Office Math. No page SVG is authored here.
"""
from pathlib import Path
import json
import matplotlib as mpl
from matplotlib.textpath import TextPath
from matplotlib.path import Path as MplPath
from matplotlib.transforms import Affine2D

mpl.rcParams['mathtext.fontset'] = 'dejavuserif'
PROJECT = Path(__file__).resolve().parent


def svg_path(path):
    commands = []
    for vertices, code in path.iter_segments(curves=True, simplify=False):
        if code == MplPath.CLOSEPOLY:
            commands.append('Z')
            continue
        letter = {MplPath.MOVETO: 'M', MplPath.LINETO: 'L',
                  MplPath.CURVE3: 'Q', MplPath.CURVE4: 'C'}[code]
        commands.append(letter + ' '.join(f'{v:.4f}' for v in vertices))
    return ' '.join(commands)


expressions = [
    # Bracing the summation symbol puts its bounds beside it, a compact
    # equivalent mathematical layout. Both limits remain explicitly present.
    ('aggregate_clr',
     r'1.8\leq\frac{{\sum}_{j=1}^{K}R_jL_j^p}{{\sum}_{j=1}^{K}L_j^p}\leq3.0',
     28, (60, 478, 590, 82)),
    ('station_repair',
     r'P_j\leftarrow\operatorname{clip}\left(\max\left\{P_j,\left[r_j^0-\beta R_jL_j^p\right]^+\right\},0,P_{\max}\right)',
     28, (60, 574, 850, 62)),
]
receipts = []
for name, latex, size, (x, y, width, height) in expressions:
    path = TextPath((0, 0), f'${latex}$', size=size, usetex=False)
    bounds = path.get_extents()
    assert bounds.width <= width and bounds.height <= height
    # SVG y points down; center vertically in the already reserved native box.
    top = y + (height - bounds.height) / 2
    positioned = path.transformed(Affine2D().scale(1, -1).translate(
        x - bounds.x0, top + bounds.y1))
    dest = PROJECT / 'figures' / f'{name}_formula.fragment.svg'
    dest.write_text(f'<path fill="#102B46" d="{svg_path(positioned)}"/>\n')
    receipts.append({'name': name, 'latex_preview': latex, 'size': size,
                     'bounds': list(positioned.get_extents().bounds),
                     'fragment': str(dest.relative_to(PROJECT)),
                     'PPTX': 'exact LaTeX marker remains native Office Math'})
(PROJECT / 'figures/formula_preview_provenance.json').write_text(
    json.dumps(receipts, indent=2) + '\n')
print('Two vector formula-preview fragments rendered; no slide files modified.')
