import json, os
from pathlib import Path
from datetime import date
from email.mime.text import MIMEText
from mcp.server.fastmcp import FastMCP
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64

mcp=FastMCP("milestone5-review-pulse")
ROOT=Path(__file__).resolve().parent; OUT=ROOT/"outputs"
PHRASE="APPROVE MILESTONE 5 OUTPUTS"; APPROVED=False
SCOPES=["https://www.googleapis.com/auth/documents","https://www.googleapis.com/auth/gmail.compose"]

def read(name):
 p=OUT/name
 return p.read_text(encoding="utf-8") if p.exists() else f"Missing {name}; run pipeline first."
def google_creds():
 token=ROOT/"token.json"; client=ROOT/"credentials.json"; creds=None
 if token.exists(): creds=Credentials.from_authorized_user_file(str(token),SCOPES)
 if creds and creds.expired and creds.refresh_token: creds.refresh(Request())
 if not creds or not creds.valid:
  if not client.exists(): raise RuntimeError("Missing credentials.json. Follow README Google setup.")
  flow=InstalledAppFlow.from_client_secrets_file(str(client),SCOPES)
  creds=flow.run_local_server(port=0)
  token.write_text(creds.to_json(),encoding="utf-8")
 return creds
def structured_record():
 r=json.loads(read("review_analysis.json"))
 sources=[]
 try:
  import csv
  with open(ROOT/"data"/"official_sources.csv",encoding="utf-8-sig",newline="") as f:
   sources=[x.get("url","") for x in csv.DictReader(f) if x.get("url")][:2]
 except: pass
 return {"date":date.today().isoformat(),"top_themes":[x.get("theme") for x in r.get("top_3_themes",[])],
  "weekly_pulse":read("weekly_product_pulse.md"),"identified_fee_issue":r.get("identified_fee_issue"),
  "explanation_bullets":read("fee_explainer.md"),"source_links":sources}

@mcp.tool()
def preview_outputs()->str:
 return "=== PRODUCT PULSE ===\n"+read("weekly_product_pulse.md")+"\n\n=== FEE EXPLAINER ===\n"+read("fee_explainer.md")
@mcp.tool()
def approve_outputs(approval_phrase:str)->str:
 global APPROVED
 if approval_phrase.strip()!=PHRASE: return "BLOCKED: exact approval phrase required: "+PHRASE
 APPROVED=True; return "APPROVED for this server session. External actions are now enabled."
@mcp.tool()
def append_to_google_doc(document_id:str)->str:
 if not APPROVED: return "BLOCKED: preview and approval are required before Google Docs action."
 creds=google_creds(); svc=build("docs","v1",credentials=creds)
 doc=svc.documents().get(documentId=document_id).execute()
 end=max(1,doc["body"]["content"][-1].get("endIndex",1)-1)
 payload="\n\n## Milestone 5 Weekly Product Pulse\n"+json.dumps(structured_record(),indent=2,ensure_ascii=False)+"\n"
 svc.documents().batchUpdate(documentId=document_id,body={"requests":[{"insertText":{"location":{"index":end},"text":payload}}]}).execute()
 return "SUCCESS: approved structured entry appended to Google Doc."
@mcp.tool()
def create_gmail_draft(to_email:str="")->str:
 if not APPROVED: return "BLOCKED: preview and approval are required before Gmail action."
 rec=structured_record()
 subject=f"Weekly Product Pulse + Customer Clarification — {rec.get('identified_fee_issue') or 'Fee issue'}"
 body=rec["weekly_pulse"]+"\n\n--- REUSABLE SUPPORT SNIPPET ---\n\n"+rec["explanation_bullets"]
 msg=MIMEText(body,"plain","utf-8"); msg["Subject"]=subject
 if to_email: msg["To"]=to_email
 raw=base64.urlsafe_b64encode(msg.as_bytes()).decode()
 svc=build("gmail","v1",credentials=google_creds())
 draft=svc.users().drafts().create(userId="me",body={"message":{"raw":raw}}).execute()
 return f"SUCCESS: Gmail draft created (draft id {draft.get('id')}). It was NOT sent."
if __name__=="__main__": mcp.run()
