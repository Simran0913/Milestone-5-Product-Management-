# Milestone 5 — AI Review Intelligence → Product Pulse → Fee Explainer → MCP

## What this prototype does
1. Collects/imports public reviews and validates the CSV.
2. Keeps the latest 12-week review window.
3. Clusters review text into at most 5 themes using TF-IDF + KMeans and ranks the top 3.
4. Extracts 3 real representative quotes from the CSV.
5. Detects one recurring fee/charge issue only when at least 2 reviews support it.
6. Generates a ≤250-word Weekly Product Pulse with 3 product actions.
7. Generates a ≤6-bullet facts-only fee explainer with 2 official links and `Last checked:`.
8. Uses MCP with an explicit approval gate before appending to Google Docs or creating a Gmail draft. Gmail is NEVER auto-sent.

## Windows setup
```bash
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run the workflow
```bash
python collect_reviews.py
python run_pipeline.py
streamlit run dashboard.py
```
If you already have a valid public reviews CSV, place it at `data/reviews.csv` with: `review_date,text,review_url,rating` (plus optional `review_id`).

## Google Docs + Gmail MCP setup
1. In Google Cloud Console, create a project.
2. Enable **Google Docs API** and **Gmail API**.
3. Configure an OAuth consent screen for your test account.
4. Create an **OAuth Desktop App** credential and download it as `credentials.json` into this project folder.
5. Run `python mcp_server.py`. The first approved Google action opens OAuth authorization and creates local `token.json`.
6. Keep `credentials.json` and `token.json` private; both are gitignored.

## Approval gate
MCP tools:
- `preview_outputs`
- `approve_outputs`
- `append_to_google_doc(document_id)`
- `create_gmail_draft(to_email="")`

Required order:
```text
Preview
  ↓
APPROVE MILESTONE 5 OUTPUTS
  ↓
Google Doc append / Gmail draft
```
Before approval, both external actions return `BLOCKED`. Approval is session-only and resets when the MCP server restarts.

## Identified fee issue
It is **derived from the current review CSV**, not hard-coded as the final result. The detector requires at least 2 supporting reviews. If the evidence threshold is not met, the project says so instead of inventing a fee issue.

## Deliverables produced
- `outputs/review_analysis.json`
- `outputs/weekly_product_pulse.md`
- `outputs/fee_explainer.md`
- `outputs/source_list.md`
- Google Doc appended entry after approval
- Gmail draft after approval (not sent)