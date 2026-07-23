#!/usr/bin/env python3
import argparse, csv, json
from collections import Counter,defaultdict
from pathlib import Path
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--input',default='data/analysis/article_market_dataset.csv'); ap.add_argument('--output',default='data/analysis/descriptive_summary.json'); a=ap.parse_args()
 with open(a.input,newline='',encoding='utf-8') as f: rows=list(csv.DictReader(f))
 by=defaultdict(list)
 for r in rows:
  if r.get('overreach_severity','')!='': by[r.get('source_type','unknown')].append(float(r['overreach_severity']))
 report={'n':len(rows),'source_type_counts':Counter(r.get('source_type','unknown') for r in rows),'mean_overreach_by_source_type':{k:sum(v)/len(v) for k,v in by.items()},'quality_missing_rate':sum(int(r.get('quality_missing','0') or 0) for r in rows)/len(rows) if rows else None}
 Path(a.output).parent.mkdir(parents=True,exist_ok=True); Path(a.output).write_text(json.dumps(report,indent=2),encoding='utf-8'); print(json.dumps(report,indent=2))
if __name__=='__main__': main()
