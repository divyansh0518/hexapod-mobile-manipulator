"""Summarize recorded simulation CSV; never interprets it as field evidence."""
import argparse,csv,json
import numpy as np
p=argparse.ArgumentParser();p.add_argument("csv");a=p.parse_args()
with open(a.csv) as f: rows=list(csv.DictReader(f))
if not rows: raise SystemExit("No samples")
print(json.dumps({"source":"kinematic simulation", "frames":len(rows),
 "minimum_ideal_support_margin_mm":min(float(r["ideal_support_margin_mm"]) for r in rows),
 "minimum_stance_legs":min(int(r["stance_legs"]) for r in rows)},indent=2))
