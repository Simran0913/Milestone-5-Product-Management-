# Milestone 5 — Beginner Guide (Windows)

You do **not** need two VS Code windows. Backend and frontend files live together in this one folder.

## What each part does
- **Backend:** `collect_reviews.py`, `validate_reviews.py`, `analyze_reviews.py`, `generate_deliverables.py`, `run_pipeline.py`
- **Frontend:** `dashboard.py` (opens in your web browser)
- **Data:** `data/reviews.csv`
- **Reports:** `outputs/`

## Easiest way to start the frontend
1. Extract this ZIP to a normal folder (for example, Downloads).
2. Open the extracted `milestone5_ready_to_use` folder in VS Code.
3. Double-click `START_DASHBOARD.bat` from Windows File Explorer. Or in VS Code terminal, run:
   `python -m streamlit run dashboard.py`
4. Wait for a browser tab. If it does not open, use the Local URL printed in the terminal, usually `http://localhost:8501`.
5. Keep the terminal window open while using the dashboard.

## Collect reviews and build reports
1. Double-click `COLLECT_AND_ANALYZE.bat`, or run these in the VS Code terminal:
   `python collect_reviews.py`
   then, if reviews were collected, `python run_pipeline.py`
2. Refresh the dashboard from its sidebar.

## Important
- Collection uses public Google Play reviews and depends on internet/platform access. It may return zero reviews.
- Do not type fake reviews into the CSV. If there are zero reviews, fix collection or use a properly sourced, clearly documented sample.
- The analysis is a keyword-based first pass, not advanced semantic clustering. Verify themes and quotes manually.
- The fee explainer is a draft; check the official links and verify exact current policy before submission.
- The MCP server is separate/optional and is not needed just to open the dashboard.

## If a command fails
Take a screenshot of the entire terminal error and ask for help. Do not close the terminal before capturing the message.
