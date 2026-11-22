"""Regression tests for verified-only real-estate research ingestion."""
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from apex.agents.property_feed import load_property_feed

TODAY = date(2026, 11, 22)


class VerifiedPropertyFeedTest(unittest.TestCase):
    def setUp(self):
        self.source = Path(__file__).resolve().parents[1] / "data" / "johnson_county_verified_properties.json"
        self.rows = json.loads(self.source.read_text(encoding="utf-8"))

    def check(self, payload):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "feed.json"
            p.write_text(json.dumps(payload), encoding="utf-8")
            return load_property_feed(path=p, today=TODAY)

    def test_real_rows(self):
        rows = self.check(self.rows)
        self.assertEqual(len(rows), 4)
        self.assertEqual(sum(x["kind"] == "vacant_land" for x in rows), 2)
        self.assertTrue(all(x["status"] == "active_as_reported" for x in rows))
        self.assertEqual(rows[0]["buyer_candidate"]["match_status"], "partial_published_criteria")

    def test_stale_fails_closed(self):
        self.assertEqual(load_property_feed(path=self.source, today=date(2026, 12, 1)), [])

    def test_buyer_claims_must_have_evidence(self):
        self.rows["properties"][0]["buyer_candidate"]["criteria_url"] = "http://example.invalid/buyer"
        self.assertEqual(self.check(self.rows), [])

    def test_no_invented_vacant_house(self):
        self.rows["properties"][2]["occupancy"] = "vacant"
        self.assertEqual(self.check(self.rows), [])

    def test_duplicate_listing_fails_closed(self):
        self.rows["properties"].append(self.rows["properties"][0])
        self.assertEqual(self.check(self.rows), [])

    def test_no_fictional_listing_or_future_date(self):
        self.rows["properties"][0]["listing_url"] = ""
        self.assertEqual(self.check(self.rows), [])
        self.rows["properties"][0]["listing_url"] = "https://www.realtor.com/example"
        self.rows["reviewed_on"] = "2026-11-23"
        self.assertEqual(self.check(self.rows), [])


if __name__ == "__main__":
    unittest.main()
