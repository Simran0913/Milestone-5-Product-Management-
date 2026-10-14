import pandas as pd
from pathlib import Path
from datetime import date,timedelta
p=Path("data/reviews.csv")
if not p.exists(): raise SystemExit("Missing data/reviews.csv; run python collect_reviews.py")
df=pd.read_csv(p)
required=["review_id","source","review_date","rating","text","review_url"]
missing=[c for c in required if c not in df.columns]
if missing: raise SystemExit(f"Missing columns: {missing}")
df["date_parsed"]=pd.to_datetime(df.review_date,errors="coerce")
df["text"]=df.text.fillna("").astype(str).str.strip()
print("REVIEW VALIDATION")
print("Rows:",len(df),"| empty text:",int((df.text=="").sum()),"| invalid dates:",int(df.date_parsed.isna().sum()),"| duplicate IDs:",int(df.review_id.duplicated().sum()))
if len(df):
 print("Date range:",df.date_parsed.min().date(),"to",df.date_parsed.max().date())
 print("Older than 84 days:",int((df.date_parsed<pd.Timestamp(date.today()-timedelta(days=84))).sum()))
print("STATUS:", "FAIL — no review rows; don't invent findings." if df.empty else "Inspect flags above; passing basic checks does not prove representativeness.")
