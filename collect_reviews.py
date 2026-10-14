import os
import time
from datetime import datetime, timedelta, timezone

import pandas as pd
from dotenv import load_dotenv
from google_play_scraper import Sort, reviews

load_dotenv()

COLUMNS = [
    "review_id",
    "source",
    "review_date",
    "rating",
    "text",
    "review_url",
    "collection_note",
]


def normalize_datetime(value):
    if not value:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def main():
    app = os.getenv("PLAY_STORE_APP_ID", "com.openai.chatgpt")
    country = os.getenv("PLAY_STORE_COUNTRY", "in")
    lang = os.getenv("PLAY_STORE_LANGUAGE", "en")

    # College requirement: public reviews from the recent 8–12 week period.
    days = int(os.getenv("REVIEW_DAYS", "84"))
    target_rows = int(os.getenv("MAX_REVIEWS", "1200"))
    page_size = int(os.getenv("REVIEW_PAGE_SIZE", "200"))
    max_scan = int(os.getenv("MAX_REVIEWS_TO_SCAN", "20000"))

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days)

    print(f"App: {app}")
    print(f"Market/language: {country}/{lang}")
    print(f"Required window: last {days} days")
    print(f"Target output rows: {target_rows}")
    print(f"Will scan up to {max_scan} public reviews if needed.")
    print()

    rows = []
    continuation_token = None
    scanned = 0
    oldest_seen = None

    while scanned < max_scan:
        batch_count = min(page_size, max_scan - scanned)

        batch, continuation_token = reviews(
            app,
            lang=lang,
            country=country,
            sort=Sort.NEWEST,
            count=batch_count,
            continuation_token=continuation_token,
        )

        if not batch:
            break

        scanned += len(batch)

        for item in batch:
            dt = normalize_datetime(item.get("at"))
            if not dt:
                continue

            if oldest_seen is None or dt < oldest_seen:
                oldest_seen = dt

            # Keep only reviews inside the requested 12-week window.
            if cutoff <= dt <= now:
                text = (item.get("content") or "").strip()
                if not text:
                    continue

                rows.append(
                    {
                        "review_id": str(item.get("reviewId") or ""),
                        "source": "Google Play - ChatGPT Android",
                        "review_date": dt.date().isoformat(),
                        "rating": item.get("score"),
                        "text": text,
                        "review_url": (
                            f"https://play.google.com/store/apps/details"
                            f"?id={app}&showAllReviews=true"
                        ),
                        "collection_note": (
                            "Public Google Play review collected from the "
                            f"last {days}-day analysis window."
                        ),
                    }
                )

        oldest_label = oldest_seen.date().isoformat() if oldest_seen else "unknown"
        print(
            f"Scanned {scanned:,} reviews | "
            f"eligible {len(rows):,} | oldest seen {oldest_label}"
        )

        # We have reached/passed the start of the requested window.
        if oldest_seen and oldest_seen <= cutoff:
            print("Reached the beginning of the requested review window.")
            break

        if continuation_token is None:
            print("No continuation token returned; collection is complete.")
            break

        time.sleep(0.15)

    df = pd.DataFrame(rows, columns=COLUMNS)

    if not df.empty:
        df = df.drop_duplicates(subset=["review_id"]).copy()
        df["review_date"] = pd.to_datetime(df["review_date"])

        # Preserve evidence across the available period instead of simply
        # taking the newest N reviews. Allocate the final sample across weeks.
        df["week"] = df["review_date"].dt.to_period("W").astype(str)

        if len(df) > target_rows:
            weeks = sorted(df["week"].unique())
            per_week = max(1, target_rows // len(weeks))

            sampled_parts = []
            for week in weeks:
                part = df[df["week"] == week]
                take = min(len(part), per_week)
                sampled_parts.append(
                    part.sample(n=take, random_state=42)
                    if len(part) > take
                    else part
                )

            sampled = pd.concat(sampled_parts, ignore_index=True)

            # Fill remaining slots from reviews not already selected.
            if len(sampled) < target_rows:
                selected_ids = set(sampled["review_id"])
                remaining = df[~df["review_id"].isin(selected_ids)]
                extra_n = min(target_rows - len(sampled), len(remaining))
                if extra_n:
                    sampled = pd.concat(
                        [
                            sampled,
                            remaining.sample(n=extra_n, random_state=42),
                        ],
                        ignore_index=True,
                    )

            df = sampled.head(target_rows)

        df = df.drop(columns=["week"], errors="ignore")
        df = df.sort_values("review_date", ascending=False)
        df["review_date"] = df["review_date"].dt.date.astype(str)

    output = Path("data/reviews.csv")
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=False, encoding="utf-8-sig")

    print()
    print(f"Saved {len(df):,} real public reviews to {output}")

    if df.empty:
        print(
            "No matching reviews were collected. Check network/app settings. "
            "Do not fabricate review evidence."
        )
        return

    dates = pd.to_datetime(df["review_date"])
    print(
        "Final CSV date range:",
        dates.min().date().isoformat(),
        "to",
        dates.max().date().isoformat(),
    )
    print("Distinct review dates:", dates.dt.date.nunique())
    print("Distinct weeks:", dates.dt.to_period("W").nunique())

    if dates.dt.to_period("W").nunique() < 2:
        print(
            "WARNING: The available sample still covers fewer than 2 distinct "
            "weeks. Increase MAX_REVIEWS_TO_SCAN and run again."
        )


if __name__ == "__main__":
    from pathlib import Path
    main()
