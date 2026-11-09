"""Fill the XX placeholders of the v14 templates from v14_summary.json (written by v14_tables.py) and the texts in
v14_texts.json (written by hand after inspecting the results). Unfilled placeholders become a visible marker."""
import json, re, sys
from pathlib import Path
M = Path(__file__).resolve().parents[2] / 'Manuscript'; R = Path(__file__).resolve().parents[1] / 'results'
texts = json.loads((R / 'v14_texts.json').read_text()) if (R / 'v14_texts.json').exists() else {}
pairs = [('paper14.template.tex', 'paper.tex'), ('v14_experiments_main.template.tex', 'v14_experiments_main.tex'),
         ('a14_F.template.tex', 'a14_F.tex'), ('a14_pointer.template.tex', 'a14_pointer.tex')]
left = []
for src, dst in pairs:
    t = (M / src).read_text()
    for k, v in texts.items():
        t = t.replace(k, v)
    for k in sorted(set(re.findall(r'XX[A-Z]+', t))):
        left.append((dst, k)); t = t.replace(k, r'\textbf{[%s pending]}' % k[2:].lower())
    (M / dst).write_text(t)
print('unfilled:', left)
