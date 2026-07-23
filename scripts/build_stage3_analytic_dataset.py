#!/usr/bin/env python3
import argparse, csv, glob, json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pmresearch.stage3.io import read_csv, read_jsonl, write_csv
CODING=['market_probability_present','probability_as_public_opinion','representativeness_caveat','market_quality_caveat','certainty_language','democratic_language','horse_race_frame','overreach_severity']
def pair_id(article_id, market_id):
 return __import__('hashlib').sha256(f'{article_id}|{market_id}'.encode()).hexdigest()[:16]
def pair_id_from_snapshot(r):
 sid=str(r.get('snapshot_id',''))
 if sid:
  parts=sid.split(':',2)
  if len(parts)==3 and parts[0] and parts[2]:
   return pair_id(parts[0], parts[2])
 aid=str(r.get('article_id','')); mid=str(r.get('market_id') or r.get('ticker',''))
 return pair_id(aid, mid) if aid and mid else ''
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--annotations',required=True); ap.add_argument('--snapshots-glob',default='data/processed/market_snapshots*_v3.jsonl'); ap.add_argument('--output',default='data/analysis/article_market_dataset.csv'); a=ap.parse_args()
 anns=read_csv(a.annotations); assert len({r['pair_id'] for r in anns})==len(anns),'duplicate adjudicated pair_id'
 snaps={}
 for p in glob.glob(a.snapshots_glob):
  for r in read_jsonl(p):
   k=str(r.get('pair_id') or pair_id_from_snapshot(r))
   if k: snaps[k]=r
 out=[]
 for r in anns:
  s=snaps.get(r['pair_id'],{}); z=dict(r)
  for f in CODING: z[f]=int(z[f]) if z.get(f,'')!='' else ''
  z['quality_evidence_class']=s.get('evidence_class',s.get('snapshot_status','unavailable')); z['price_at_publication']=s.get('price_at_publication',s.get('price','')); z['trade_count_window']=s.get('trade_count_window',s.get('trade_count','')); z['volume_window']=s.get('volume_window',s.get('trailing_volume','')); z['spread_at_publication']=s.get('spread_at_publication',s.get('relative_spread','')); z['quality_missing']=int(not any(z.get(k) not in (None,'') for k in ['trade_count_window','volume_window','spread_at_publication']))
  out.append(z)
 fields=list(out[0]) if out else list(anns[0]) if anns else ['pair_id']; write_csv(a.output,out,fields); print(json.dumps({'rows':len(out),'output':a.output}))
if __name__=='__main__': main()
