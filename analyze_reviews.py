import json,re
from pathlib import Path
from datetime import date,timedelta
import pandas as pd

INPUT=Path('data/reviews.csv'); OUT=Path('outputs/review_analysis.json')
THEMES={
 'Image generation / editing':[r'\bimage\b',r'\bimages\b',r'\bphoto\b',r'\bphotos\b',r'\bpicture\b',r'\bgenerat',r'\bedit'],
 'Answer quality / accuracy':[r'\bwrong\b',r'\bincorrect',r'\binaccur',r'\banswer',r'\bresponse',r'\baccur',r'\bmistake',r'\bhallucin'],
 'Usage limits / upgrade':[r'\blimit',r'\bquota',r'\bupgrade',r'\bpaid\b',r'\bpay\b',r'\bplus\b',r'\bsubscription',r'\bprice'],
 'Reliability / performance':[r'\bcrash',r'\bbug',r'\berror',r'\bslow\b',r'\blag',r'\bfreeze',r'\bloading\b',r'\bnot work',r"\bdoesn.?t work",r'\bstopped\b'],
 'Voice experience':[r'\bvoice\b',r'\bspeech\b',r'\bmicrophone\b',r'\bmic\b',r'\bspeak',r'\baudio\b',r'\bdictat'],
}
FEE_PATTERNS=[
 r'\blimit.*\b(pay|paid|upgrade|plus|subscription)',
 r'\b(pay|paid|upgrade|plus|subscription).*\blimit',
 r'\bupgrade.*\b(pay|paid|price|subscription)',
 r'\b(pay|paid|price).*\bupgrade',
 r'\bfree.*\b(pay|paid|upgrade|limit)',
 r'\b(pay|paid|upgrade|limit).*\bfree',
]

def matches(text,patterns):
 return any(re.search(p,str(text),re.I) for p in patterns)

def representative_quote(group,patterns):
 # Prefer detailed negative/constructive evidence over one-word praise.
 g=group.copy()
 g['_signal']=g.text.apply(lambda x:sum(bool(re.search(p,str(x),re.I)) for p in patterns))
 g['_len']=g.text.astype(str).str.len().clip(upper=500)
 g['_neg']=(g.rating.fillna(3)<=3).astype(int)
 g['_score']=g['_signal']*1000+g['_neg']*100+g['_len']
 return g.sort_values(['_score','review_date'],ascending=[False,False]).iloc[0]

def main():
 if not INPUT.exists(): raise SystemExit('Missing data/reviews.csv')
 df=pd.read_csv(INPUT)
 need={'review_date','text','review_url','rating'}
 if not need.issubset(df.columns): raise SystemExit(f'CSV needs {sorted(need)}')
 df['text']=df.text.fillna('').astype(str).str.strip()
 df['review_date']=pd.to_datetime(df.review_date,errors='coerce')
 df=df[(df.text!='')&df.review_date.notna()].copy()
 if df.empty: raise SystemExit('No usable reviews.')
 newest=df.review_date.max(); df=df[df.review_date>=newest-timedelta(weeks=12)].copy()

 clusters=[]
 matched={}
 for cid,(theme,patterns) in enumerate(THEMES.items()):
  mask=df.text.apply(lambda x:matches(x,patterns))
  matched[theme]=df[mask].copy()
  clusters.append({'cluster_id':cid,'theme':theme,'review_count':int(mask.sum()),
                   'method':'keyword-guided thematic clustering from review text'})
 clusters=sorted(clusters,key=lambda x:x['review_count'],reverse=True)
 top=clusters[:3]

 quotes=[]
 for c in top:
  g=matched[c['theme']]
  if g.empty: continue
  r=representative_quote(g,THEMES[c['theme']])
  quotes.append({'quote':str(r.text)[:1000],'date':r.review_date.date().isoformat(),
   'rating':None if pd.isna(r.rating) else int(r.rating),'source_url':str(r.review_url),
   'review_id':str(r.get('review_id','')),'theme':c['theme']})

 fee_mask=df.text.apply(lambda x:matches(x,FEE_PATTERNS)); fee_count=int(fee_mask.sum())
 fee_issue='Usage limits and paid-upgrade confusion' if fee_count>=2 else None
 fee_evidence=[]
 if fee_issue:
  fg=df[fee_mask].copy(); fg['_len']=fg.text.astype(str).str.len()
  for _,r in fg.sort_values(['_len','review_date'],ascending=[False,False]).head(5).iterrows():
   fee_evidence.append({'quote':str(r.text)[:1000],'date':r.review_date.date().isoformat(),
    'rating':None if pd.isna(r.rating) else int(r.rating),'source_url':str(r.review_url),
    'review_id':str(r.get('review_id',''))})

 report={'generated_date':date.today().isoformat(),'review_count':int(len(df)),
  'date_range':{'start':df.review_date.min().date().isoformat(),'end':df.review_date.max().date().isoformat()},
  'method':'Keyword-guided thematic clustering over recent public review text. Reviews may match more than one theme; at most five themes are reported.',
  'theme_clusters':clusters[:5],'top_3_themes':top,'three_real_review_quotes':quotes,
  'identified_fee_issue':fee_issue,'fee_issue_match_count':fee_count,'fee_issue_evidence':fee_evidence,
  'fee_issue_status':f'Recurring issue detected in {fee_count} reviews: {fee_issue}' if fee_issue else 'No recurring fee/charge issue met the minimum evidence threshold of 2 reviews.'}
 OUT.parent.mkdir(exist_ok=True); OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
 print('Saved',OUT); print('Reviews analyzed:',len(df)); print('Top 3 themes:')
 for x in top: print(f"- {x['theme']} ({x['review_count']})")
 print('Real quotes extracted:',len(quotes)); print(report['fee_issue_status'])
if __name__=='__main__': main()
