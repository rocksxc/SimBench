import sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import forest_engine_v14 as fe, capdesign as cd
orig = cd.Engine.colgen
def timed(self, r, start, **kw):
    t0 = time.time(); out = orig(self, r, start, **kw)
    print('  colgen r=%d beta=%s iters %d ints %d %.1fs opt %s up %.6g lo %.6g' % (r, kw.get('beta', 0), out['iterations'], len(out['interviews']), time.time() - t0, out['optimal'], out['upper'], out['lower']), flush=True)
    return out
cd.Engine.colgen = timed
t0 = time.time()
r = fe.run_task('WDBC', 20261108, 9, 4, '/tmp/claude-0/-home-user-SimBench/3b198ae7-bda9-5880-b22e-39bc53bf11f2/scratchpad/inputs_v11', fitted=True)
print('total %.1fs' % (time.time() - t0), r['ratio_exact_lower'], r.get('ratio_fitted'))
