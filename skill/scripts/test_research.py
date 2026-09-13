"""Check discovery eligibility and shortlist coverage without network requests."""
import argparse
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

import research


class FakeFetcher:
    def __init__(self):
        self.requests, self.errors = [], []
        self.network_attempts = 0

    def get(self, endpoint):
        self.network_attempts += 1
        query = parse_qs(urlsplit(endpoint).query)["q"][0]
        self.requests.append({"query": query})
        prefix = "skills" if query.startswith("skills") else "plugins"
        return {"items": [{"full_name": f"{prefix}/one"}, {"full_name": f"{prefix}/two"}]}


class DiscoveryTests(unittest.TestCase):
    def collect(self, mode="resources", repos=None):
        with tempfile.TemporaryDirectory() as folder:
            args = argparse.Namespace(out=folder, days=30, as_of="2026-01-30", mode=mode,
                                      max_requests=100, retries=1, repo=repos or [],
                                      query=["skills", "plugins"], limit=2)
            fetcher = FakeFetcher()
            def enrich(repo, fetcher, window, discovery):
                return {"repo": repo, "discovery": discovery, "verification_status": "unverified"}, []
            with patch.object(research, "enrich", side_effect=enrich):
                manifest = research.run(args, fetcher)
            data = json.loads((Path(folder) / "candidates.json").read_text())
            return manifest, data["candidates"]

    def test_evergreen_resources_remain_eligible_and_queries_share_shortlist(self):
        manifest, candidates = self.collect()
        self.assertTrue(all("pushed:" not in q for q in manifest["queries"]))
        self.assertEqual([c["repo"] for c in candidates], ["skills/one", "plugins/one"])
        self.assertTrue(all(c["verification_status"] == "unverified" for c in candidates))

    def test_news_mode_retains_inclusive_activity_window(self):
        manifest, candidates = self.collect("news")
        self.assertTrue(all("pushed:2026-01-01..2026-01-30" in q for q in manifest["queries"]))
        self.assertEqual(candidates[0]["discovery"][0]["basis"], "repository_pushed_search_not_launch")

    def test_explicit_repository_bypasses_discovery_in_both_modes(self):
        for mode in ("resources", "news"):
            manifest, candidates = self.collect(mode, ["owner/repo"])
            self.assertEqual(manifest["queries"], [])
            self.assertEqual(candidates[0]["repo"], "owner/repo")


if __name__ == "__main__":
    unittest.main()
