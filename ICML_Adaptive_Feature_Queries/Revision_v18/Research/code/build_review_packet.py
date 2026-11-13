"""Build the review packet (clean text + 100 dpi page PNGs) from a PDF, as in Revision_v12/Reviews/README.md."""
import sys, re
from pathlib import Path
import pymupdf as fitz
pdf, out = Path(sys.argv[1]), Path(sys.argv[2]); (out / 'pages').mkdir(parents=True, exist_ok=True)
doc = fitz.open(pdf); txt = []
for i, p in enumerate(doc):
    txt.append('\n\n===== PAGE %d =====\n' % (i + 1)); txt.append(p.get_text())
    p.get_pixmap(dpi=100).save(out / 'pages' / ('p%02d.png' % (i + 1)))
clean = '\n'.join(l for l in ''.join(txt).split('\n') if not re.fullmatch(r'\d{3}', l.strip()))
(out / 'paper_clean.txt').write_text(clean); print('pages', len(doc), 'chars', len(clean))
