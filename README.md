# Milestone 5 – ChatGPT Review Pulse

## About My Project

For Milestone 5, I built a prototype called **ChatGPT Review Pulse**.

The idea behind this project is simple: there are a large number of public user reviews for ChatGPT, and it can be difficult for a Product Manager to manually read all of them and understand what users are repeatedly talking about.

My prototype collects recent public reviews of the ChatGPT Android app, analyzes the feedback, identifies common themes, and converts the findings into a short Weekly Product Pulse.

I also added an approval step before the final output can be used for external actions such as updating a Google Doc or preparing a Gmail draft.

---

## What I Wanted to Solve

As a Product Manager, reading hundreds or thousands of reviews manually every week is not practical.

I wanted to build a workflow that could help me answer questions such as:

- What are users talking about most?
- What problems are appearing repeatedly?
- What are some real examples of user feedback?
- Is there any recurring confusion around usage limits, subscriptions, or payments?
- What product actions should I consider based on this feedback?

The purpose is not to replace Product Manager judgement. The analysis gives me a starting point, and I review the output before taking any external action.

---

## My Review Dataset

For the current prototype, I collected **1,200 public reviews** of the ChatGPT Android app.

The current sample contains reviews from:

**08 October 2026 to 11 October 2026**

The collector checks reviews against a recent review window. Because ChatGPT receives a high volume of reviews, the latest 1,200 usable reviews in this run are concentrated within these recent dates.

I kept the real review text so that the themes and quotes shown in the prototype can be traced back to actual review data.

---

## How My Workflow Works

My workflow follows these steps:

1. I collect public ChatGPT Android reviews and store them in a CSV file.
2. I validate the review data before starting the analysis.
3. Similar feedback is grouped into a maximum of five themes.
4. I identify the top three themes based on the review evidence.
5. I select three representative quotes from the real review data.
6. I check for recurring confusion related to usage limits, upgrades, subscriptions, fees, or charges.
7. I generate a Weekly Product Pulse of no more than 250 words.
8. I generate a short facts-only customer clarification / Fee Explainer using official sources.
9. I review the generated output before approving any external action.
10. After approval, the workflow can append the result to Google Docs and prepare a Gmail draft. The email is not automatically sent.

---

## Review Analysis

For text analysis, I used Python-based text processing and clustering.

The workflow uses review text to identify repeated patterns and organizes the feedback into a maximum of five themes. The three strongest themes are then used in the Product Pulse.

I also kept representative user quotes in the analysis so that the final summary is supported by real customer feedback rather than invented examples.

The generated analysis can be found in:

`outputs/review_analysis.json`

---

## Weekly Product Pulse

The prototype generates a short **Weekly Product Pulse** based on the review analysis.

It contains:

- the main review themes,
- supporting customer quotes,
- an important product observation, and
- exactly three product action ideas.

I intentionally keep the Product Pulse short so that it can be quickly reviewed by a Product Manager.

Output:

`outputs/weekly_product_pulse.md`

---

## Recurring Customer Confusion

In my current analysis, the workflow detected recurring feedback around **usage limits and paid-upgrade confusion**.

The issue is only reported when multiple reviews provide supporting evidence. I did this so that the workflow does not create a fee or subscription issue when the review data does not support one.

The related customer clarification is written using neutral, factual language and official sources.

Output:

`outputs/fee_explainer.md`

---

## Official Sources

For customer-facing clarification, I use official OpenAI Help Center sources rather than relying only on review comments.

The source information used by the prototype is stored in:

`data/official_sources.csv`

and the generated source list is available in:

`outputs/source_list.md`

The Fee Explainer also includes a **Last checked** date so it is clear when the information was reviewed.

---

## Human Approval Before External Actions

One part of this milestone that I wanted to make clear was that generating an analysis and taking an external action are two different things.

The workflow can prepare the output first, but an external action should not happen automatically.

I therefore added an approval gate.

Before approval, actions such as updating Google Docs or creating a Gmail draft should remain blocked.

The approval phrase used in my prototype is:

`APPROVE MILESTONE 5 OUTPUTS`

After approval, the workflow can:

- append the structured Product Pulse information to a Google Doc, and
- create a Gmail draft with the customer clarification.

The Gmail message is created as a **draft only**. It is not automatically sent.

---

## Google Docs + Gmail Setup

For the external-action part of the prototype, I use Google APIs.

The setup requires:

1. Creating a project in Google Cloud Console.
2. Enabling the Google Docs API.
3. Enabling the Gmail API.
4. Configuring OAuth consent.
5. Creating OAuth credentials for a Desktop application.
6. Saving the downloaded credentials as `credentials.json` in the project folder.
7. Providing the Google Document ID that should receive the approved output.

Sensitive credential files are not intended to be uploaded to the public GitHub repository.

---

## How I Run the Project

I created the project in Python and used Streamlit for the prototype dashboard.

After setting up the Python environment and installing the requirements, I run:

```bash
python collect_reviews.py