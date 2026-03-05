#!/usr/bin/env python3
"""
fetch_feed.py — Daily market & news feed aggregator.

Run directly:         python fetch_feed.py
Via Task Scheduler:   run_feed.bat handles this automatically.

Output files are written to the output/ directory and (optionally)
pushed to GitHub so downstream projects can fetch them via raw URL.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import feedparser
import yfinance as yf

from config import (
    ASSETS,
    AUTO_GIT_PUSH,
    JSON_FILENAME,
    MAX_NEWS_ITEMS,
    MAX_SCAN_PER_FEED,
    MD_FILENAME,
    NEWS_FEEDS,
    NEWS_KEYWORDS,
    OUTPUT_DIR,
)

SCRIPT_DIR = Path(__file__).parent.resolve()


# =============================================================================
# PRICES
# =============================================================================

def fetch_prices() -> dict:
    """
    Fetch the latest closing price and day-over-day change for every ticker
    in ASSETS. Uses 5 days of history so weekends/holidays don't cause gaps.
    """
    results = {}

    for category, tickers in ASSETS.items():
        results[category] = {}

        for name, ticker in tickers.items():
            print(f"    {name} ({ticker}) ...", end=" ", flush=True)
            try:
                hist = yf.Ticker(ticker).history(period="5d")
                hist = hist.dropna(subset=["Close"])

                if hist.empty:
                    raise ValueError("No data returned from Yahoo Finance")

                latest_price = hist["Close"].iloc[-1]
                prev_price   = hist["Close"].iloc[-2] if len(hist) >= 2 else None

                change     = round(latest_price - prev_price, 6) if prev_price else None
                pct_change = round(change / prev_price * 100, 3) if prev_price else None
                price      = round(latest_price, 6)
                date_str   = hist.index[-1].strftime("%Y-%m-%d")

                results[category][name] = {
                    "ticker":     ticker,
                    "price":      price,
                    "change":     change,
                    "pct_change": pct_change,
                    "date":       date_str,
                }

                change_display = f"{pct_change:+.2f}%" if pct_change is not None else "n/a"
                print(f"{price:,.4f}  ({change_display})")

            except Exception as exc:
                results[category][name] = {"ticker": ticker, "error": str(exc)}
                print(f"ERROR — {exc}")

    return results


# =============================================================================
# NEWS
# =============================================================================

def _matched_keywords(text: str) -> list:
    """Return list of NEWS_KEYWORDS found in text (lowercase match)."""
    text_lower = text.lower()
    return [kw for kw in NEWS_KEYWORDS if kw in text_lower]


def fetch_news() -> list:
    """
    Pull configured RSS feeds, filter headlines by keyword relevance,
    deduplicate across sources, and return up to MAX_NEWS_ITEMS items.
    """
    candidates = []

    for feed_cfg in NEWS_FEEDS:
        print(f"    {feed_cfg['name']} ...", end=" ", flush=True)
        try:
            feed = feedparser.parse(feed_cfg["url"])
            matched_count = 0

            for entry in feed.entries[:MAX_SCAN_PER_FEED]:
                title   = entry.get("title", "").strip()
                summary = entry.get("summary", "").strip()
                matched = _matched_keywords(f"{title} {summary}")

                if matched:
                    candidates.append({
                        "source":           feed_cfg["name"],
                        "title":            title,
                        "link":             entry.get("link", ""),
                        "published":        entry.get("published", ""),
                        "matched_keywords": matched[:4],
                    })
                    matched_count += 1

            print(f"{matched_count} matched")

        except Exception as exc:
            print(f"ERROR — {exc}")

    # Deduplicate: skip headlines whose first 50 chars match something already seen.
    # This handles the same story being syndicated across multiple feeds.
    seen, unique = set(), []
    for item in candidates:
        key = item["title"][:50].lower()
        if key not in seen:
            seen.add(key)
            unique.append(item)

    return unique[:MAX_NEWS_ITEMS]


# =============================================================================
# MARKDOWN OUTPUT
# =============================================================================

_CATEGORY_LABELS = {
    "commodities": "Commodities",
    "fx":          "FX",
    "indices":     "Indices",
    "stocks":      "Stocks",
}


def build_markdown(data: dict) -> str:
    date_str = data["generated_at"][:10]

    lines = [
        f"# Daily Feed — {date_str}",
        f"*Generated: {data['generated_at']} UTC*",
        "",
        "---",
        "",
        "## Markets",
        "",
    ]

    for cat_key, cat_label in _CATEGORY_LABELS.items():
        cat_data = data["prices"].get(cat_key)
        if not cat_data:
            continue

        lines += [f"### {cat_label}", ""]
        lines += [
            "| Asset | Price | Change | % Change |",
            "|:------|------:|------:|---------:|",
        ]

        for name, info in cat_data.items():
            if "error" in info:
                lines.append(f"| {name} | — | — | ⚠ data unavailable |")
            else:
                direction = "▲" if (info["change"] or 0) >= 0 else "▼"
                lines.append(
                    f"| {name} "
                    f"| {info['price']:>12,.4f} "
                    f"| {direction} {abs(info['change'] or 0):,.4f} "
                    f"| {(info['pct_change'] or 0):+.2f}% |"
                )

        lines.append("")

    lines += ["---", "", "## Key Global Headlines", ""]

    if data["news"]:
        for h in data["news"]:
            kw_str = ", ".join(h["matched_keywords"])
            lines.append(f"**[{h['source']}]** {h['title']}")
            lines.append(f"*Tags: {kw_str}*")
            if h.get("link"):
                lines.append(f"{h['link']}")
            lines.append("")
    else:
        lines.append("*No significant headlines matched the keyword filter today.*")

    lines += [
        "---",
        f"*Filter: {len(NEWS_KEYWORDS)} keywords active · "
        f"Sources: {', '.join(f['name'] for f in NEWS_FEEDS)}*",
    ]

    return "\n".join(lines)


# =============================================================================
# GIT PUSH
# =============================================================================

def git_push(output_dir: str) -> None:
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    try:
        subprocess.run(["git", "add", output_dir], cwd=SCRIPT_DIR, check=True)

        # Check if there's actually anything staged before committing
        diff_result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=SCRIPT_DIR
        )
        if diff_result.returncode == 0:
            print("  Git: nothing new to commit.")
            return

        subprocess.run(
            ["git", "commit", "-m", f"feed: daily update {date_str}"],
            cwd=SCRIPT_DIR,
            check=True,
        )
        subprocess.run(["git", "push"], cwd=SCRIPT_DIR, check=True)
        print("  Git: pushed successfully.")

    except subprocess.CalledProcessError as exc:
        print(f"  Git error: {exc}", file=sys.stderr)
        print("  Check that git is configured and the remote is reachable.", file=sys.stderr)


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:
    now = datetime.now(timezone.utc)
    print(f"\n{'=' * 55}")
    print(f"  Daily Feed  —  {now.strftime('%Y-%m-%d  %H:%M UTC')}")
    print(f"{'=' * 55}\n")

    # --- Prices ---
    print("[1/3] Fetching prices...\n")
    prices = fetch_prices()

    # --- News ---
    print("\n[2/3] Fetching & filtering news...\n")
    news = fetch_news()

    # --- Assemble data ---
    data = {
        "generated_at": now.isoformat(timespec="seconds"),
        "prices":        prices,
        "news":          news,
    }

    # --- Write output ---
    out_dir = SCRIPT_DIR / OUTPUT_DIR
    out_dir.mkdir(exist_ok=True)

    json_path = out_dir / JSON_FILENAME
    md_path   = out_dir / MD_FILENAME

    json_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    md_path.write_text(build_markdown(data), encoding="utf-8")

    print(f"\n[3/3] Output written:")
    print(f"  {json_path}")
    print(f"  {md_path}")

    # --- Git push ---
    if AUTO_GIT_PUSH:
        print("\nPushing to GitHub...")
        git_push(OUTPUT_DIR)

    print("\nDone.\n")


if __name__ == "__main__":
    main()
