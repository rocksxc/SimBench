# Table "laws": exact population-level quantities for Beta laws of the agreement share (no data, no sampling).
import numpy as np, sys, json
from scipy.special import betaln, gammaln
from scipy.stats import beta as betad, binom
import fewannot as fa

def beta_count_law(n, a, b):
    j = np.arange(n + 1)
    return np.exp(gammaln(n + 1) - gammaln(j + 1) - gammaln(n - j + 1) + betaln(a + j, b + n - j) - betaln(a, b))

def ceiling_beta(a, b):
    m = a / (a + b)
    return m * betad.sf(0.5, a + 1, b) + (1 - m) * betad.cdf(0.5, a, b + 1)

def mislabel_beta(n, a, b):
    from scipy.integrate import quad
    f = lambda z: (binom.sf(n // 2, n, z) if z < 0.5 else binom.cdf(n // 2, n, z)) * betad.pdf(z, a, b)
    return quad(f, 0, 0.5, limit=200)[0] + quad(f, 0.5, 1, limit=200)[0]

xs, above, below = fa.make_grid(0.5)
rows = []; out = {}
laws = [(2.2, 2.2, "Beta(2.2, 2.2)"), (1.2, 0.9, "Beta(1.2, 0.9)"), (0.4, 0.4, "Beta(0.4, 0.4)")]
for a, b, name in laws:
    g = betad.pdf(0.5, a, b); truth = betad.sf(0.5, a, b); ceil = ceiling_beta(a, b)
    for n in (3, 5, 9, 15):
        q = beta_count_law(n, a, b)
        lo, hi = fa.idset(q, n, above.astype(float), xs)
        clo, chi = fa.idset(q, n, np.maximum(xs, 1 - xs), xs)
        k = np.arange(n + 1); plug = (q * np.maximum(k, n - k) / n).sum()
        mis = mislabel_beta(n, a, b)
        r = dict(law=name, n=n, g=g, lo=lo, hi=hi, width=hi - lo, law_width=np.pi * g / n, ratio=(hi - lo) * n / (np.pi * g),
                 mis=mis, mis_law=g / np.sqrt(2 * np.pi * n), ceil=ceil, clo=clo, chi=chi, cwidth=chi - clo,
                 plug=plug, bias=plug - ceil, bias_law=g / (4 * n), plug_outside=bool(plug > chi + 1e-9), truth=truth)
        rows.append(r)
        print({k2: (round(v, 4) if isinstance(v, float) else v) for k2, v in r.items()})
json.dump(rows, open("../results/tab_laws.json", "w"), indent=1)
with open("../Manuscript/gen/tab_laws.tex", "w") as fh:
    fh.write("\\begin{tabular}{@{}llccccccc@{}}\n\\toprule\n")
    fh.write(" & & \\multicolumn{3}{c}{consensus agreement $A_\\infty$} & \\multicolumn{4}{c}{ceiling $C$}\\\\\n\\cmidrule(lr){3-5}\\cmidrule(l){6-9}\n")
    fh.write("law of $\\pi$ & $n$ & $\\Pr(E_n)$ & width $U-L$ & $\\pi g(\\frac12)/n$ & width & plug-in bias & $g(\\frac12)/(4n)$ & plug-in excluded\\\\\n\\midrule\n")
    for i, r in enumerate(rows):
        nm = r["law"] if r["n"] == 3 else ""
        fh.write(f"{nm} & {r['n']} & {r['mis']:.3f} & {r['width']:.3f} & {r['law_width']:.3f} & {r['cwidth']:.4f} & {r['bias']:.4f} & {r['bias_law']:.4f} & {'yes' if r['plug_outside'] else 'no'}\\\\\n")
        if r["n"] == 15 and i < len(rows) - 1: fh.write("\\addlinespace\n")
    fh.write("\\bottomrule\n\\end{tabular}\n")
