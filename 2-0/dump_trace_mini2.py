# -*- coding: utf-8 -*-
"""Прогон MuJoCo стенда v2 (sim_mini2.py) с записью движения в trace_mini2.json — для окна view_mini2.py.
Два прогона: мотор 0.2 Н·м (крутит) и мотор 0.05 Н·м (срывается под пальцем 3 Н)."""
import json
src = open("sim_mini2.py", encoding="utf-8").read()
exec(src.split('print("\n=== MuJoCo: мотор крутит')[0].replace("print(", "(lambda *a, **k: None)("))
out = {}
for key, tl in (("strong", 0.2), ("weak", 0.05)):
    run(tl, turns=2, rps=0.5)
    gap = max(r[5] for r in TRACE)
    print(key, "расхождение шарнира шатун-плечо: макс %.4f мм" % gap)
    out[key] = {"t_lim": tl, "force": F, "gap_max_mm": gap,
                "trace": [[round(t, 4), c, a, f, lk] for t, c, a, f, lk, g in TRACE[::50]]}
json.dump(out, open("trace_mini2.json", "w"))
print("ok", {k: len(v["trace"]) for k, v in out.items()})
