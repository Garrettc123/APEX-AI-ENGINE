"""Inspect verified local property research without web scraping or side effects.

Usage: python -m scripts.property_research_report
       python -m scripts.property_research_report --json
No buyer or seller messages, payments or offers are generated.
"""
import argparse
import csv
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from apex.agents.property_feed import load_property_feed  # noqa: E402


def build_report(rows):
    report = []
    for row in rows:
        buyer = row.get("buyer_candidate") or {}
        report.append({
            "property_id": row["id"],
            "address": row["address"],
            "kind": row["kind"],
            "asking_price_usd": row["asking_price_usd"],
            "listing_url": row["listing_url"],
            "buyer_candidate": buyer.get("name", ""),
            "buy_box_criteria_url": buyer.get("criteria_url", ""),
            "fit_status": buyer.get("match_status", "not_matched"),
            "reviewed_on": row["reviewed_on"],
            "seller_authorized": False,
            "buyer_committed": False,
            "profit_verified": False,
            "next_check": row.get("exclusion") or (
                "Confirm buyer interest, property access, utilities, title, repairs, seller authority and contract rights."
            ),
        })
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Output structured research JSON, not a deal agreement")
    parser.add_argument("--as-of", type=date.fromisoformat, default=None, help="Date for freshness validation (YYYY-MM-DD)")
    args = parser.parse_args()
    rows = load_property_feed(today=args.as_of)
    report = build_report(rows)
    if args.json:
        print(json.dumps({"research_only": True, "candidate_count": len(report), "properties": report}, indent=2))
    elif report:
        writer = csv.DictWriter(sys.stdout, fieldnames=list(report[0]))
        writer.writeheader()
        writer.writerows(report)
    else:
        print("No fresh verified records: feed absent, invalid or older than 7 days.", file=sys.stderr)
    return 0 if report else 1


if __name__ == "__main__":
    raise SystemExit(main())
