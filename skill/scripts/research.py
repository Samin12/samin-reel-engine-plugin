#!/usr/bin/env python3
"""Collect GitHub story leads and visual references; never certify product claims.

python3 research.py discover --days 30 --as-of 2026-09-04 --out work/research
python3 research.py --repo moonshine-ai/moonshine --out work/moonshine
Only Python's standard library is required. gh, when installed, supplies auth.
"""
import argparse
import base64
import json
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

DEFAULT_QUERIES = ["claude code", "ai agent", "mcp"]
TRACKING = {"fbclid", "gclid", "dclid", "mc_cid", "mc_eid"}


def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def calendar_window(days, as_of, today=None):
    upper = date.fromisoformat(as_of)
    if not 1 <= days <= 366 or upper > (today or datetime.now(timezone.utc).date()):
        raise ValueError("days must be 1..366 and as-of cannot be in the future (UTC)")
    return {"lower_date": (upper - timedelta(days=days - 1)).isoformat(),
            "upper_date": upper.isoformat(), "days": days, "inclusive": True, "timezone": "UTC"}


def classify_date(value, window):
    result = {"raw_date": value, "date": None, "window_status": "unknown", "rejected_future": False}
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo:
            parsed = parsed.astimezone(timezone.utc)
        day = parsed.date().isoformat()
    except (AttributeError, TypeError, ValueError):
        return result
    result.update(date=day, window_status="in-window" if window["lower_date"] <= day <= window["upper_date"] else "outside",
                  rejected_future=day > window["upper_date"])
    return result


def clean_url(value):
    parsed = urllib.parse.urlsplit(value.strip())
    params = [(k, v) for k, v in urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
              if not k.lower().startswith("utm_") and k.lower() not in TRACKING]
    return urllib.parse.urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path,
                                   urllib.parse.urlencode(params), parsed.fragment))


def canonical_repo(value):
    value = value.strip()
    if "://" in value:
        parsed = urllib.parse.urlsplit(value)
        if parsed.hostname not in ("github.com", "www.github.com"):
            raise ValueError("repo must be OWNER/NAME or a github.com repository URL")
        value = "/".join(parsed.path.strip("/").split("/")[:2])
    value = re.sub(r"\.git$", "", value.strip("/"), flags=re.I)
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", value):
        raise ValueError("invalid GitHub repository: " + value)
    return value.lower()


def visual_references(markdown, repo, branch, readme_path, source_url):
    base = "https://raw.githubusercontent.com/{}/{}/{}".format(repo, branch, readme_path)
    found = [(label, url, "image") for label, url in re.findall(r'!\[([^\]]*)\]\(<?([^\s)>]+)>?', markdown)]
    definitions = {" ".join(key.lower().split()): url for key, url in
                   re.findall(r'^\s{0,3}\[([^\]]+)\]:\s*<?([^\s>]+)>?', markdown, re.M)}
    for label, key in re.findall(r'!\[([^\]]*)\](?:\[([^\]]*)\])?(?!\()', markdown):
        url = definitions.get(" ".join((key or label).lower().split()))
        if url:
            found.append((label, url, "image"))
    found += [("", url, "image") for url in re.findall(r'<(?:img|source)\b[^>]*?src=["\']([^"\']+)', markdown, re.I)]
    found += [("", url, "demo") for url in re.findall(r'<video\b[^>]*?src=["\']([^"\']+)', markdown, re.I)]
    for label, url in re.findall(r'(?<!!)\[([^\]]+)\]\(<?([^\s)>]+)>?', markdown):
        if re.search(r"demo|video", label, re.I) or re.search(r"youtube\.com|youtu\.be|vimeo\.com|\.(mp4|webm|mov)(?:[?#]|$)", url, re.I):
            found.append((label, url, "demo"))
    result = {}
    for label, original, kind in found:
        if re.search(r"\.(mp4|webm|mov)(?:[?#]|$)", original, re.I):
            kind = "demo"
        target = original
        if original.startswith("/") and not original.startswith("//"):
            target = "https://raw.githubusercontent.com/{}/{}/{}".format(repo, branch, original.lstrip("/"))
        url = clean_url(urllib.parse.urljoin(base, target))
        if urllib.parse.urlsplit(url).scheme not in ("https", "http"):
            continue
        result.setdefault(url, {"candidate_url": "https://github.com/" + repo, "url": url,
                                "original_url": original, "label": label, "kind": kind,
                                "source_url": source_url, "capture_status": "not_captured",
                                "rights_status": "not_assessed"})
    return list(result.values())


class SourceError(Exception):
    def __init__(self, message, kind="request_error", retryable=False):
        super().__init__(message)
        self.kind, self.retryable = kind, retryable


class Fetcher:
    def __init__(self, out, max_requests=100, retries=1):
        self.raw = Path(out) / "raw"
        self.raw.mkdir(parents=True, exist_ok=True)
        self.max_requests, self.retries = max_requests, retries
        self.requests, self.errors = [], []
        self.network_attempts = 0
        self.gh = shutil.which("gh")

    def _request(self, endpoint):
        if self.gh:
            proc = subprocess.run([self.gh, "api", "--hostname", "github.com", "-X", "GET", endpoint],
                                  capture_output=True, text=True, timeout=20)
            if proc.returncode:
                message = proc.stderr.strip()[:1000]
                kind = "rate_limit" if "rate limit" in message.lower() or "HTTP 429" in message else "http_error"
                raise SourceError(message, kind, bool(re.search(r"HTTP 5\d\d", message)))
            return json.loads(proc.stdout)
        request = urllib.request.Request("https://api.github.com/" + endpoint,
                                         headers={"Accept": "application/vnd.github+json", "User-Agent": "reel-research-engine/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            message = exc.read(2000).decode("utf-8", "replace")
            kind = "rate_limit" if exc.code == 429 or "rate limit" in message.lower() else "http_error"
            raise SourceError(f"HTTP {exc.code}: {message}", kind, exc.code >= 500) from exc

    def get(self, endpoint):
        url = "https://api.github.com/" + endpoint
        for attempt in range(self.retries + 1):
            entry = {"url": url, "retrieved_at_utc": utc_now(), "attempt": attempt + 1}
            try:
                if self.network_attempts >= self.max_requests:
                    raise SourceError("run request budget exhausted", "request_budget")
                self.network_attempts += 1
                entry["network_attempted"] = True
                data = self._request(endpoint)
                entry["status"] = "success"
                raw_path = self.raw / f"request-{len(self.requests) + 1:03}.json"
                raw_path.write_text(json.dumps({**entry, "payload": data}, indent=2) + "\n")
                entry["raw_file"] = str(raw_path.relative_to(self.raw.parent))
                self.requests.append(entry)
                return data
            except (SourceError, subprocess.TimeoutExpired, urllib.error.URLError, OSError, ValueError) as exc:
                kind = getattr(exc, "kind", "invalid_json" if isinstance(exc, ValueError) else "transport_error")
                entry.setdefault("network_attempted", False)
                entry.update(status="error", error_kind=kind, message=str(exc)[:1000])
                self.requests.append(entry)
                if attempt < self.retries and getattr(exc, "retryable", False):
                    continue  # One immediate transient-server retry; never sleep on rate limits.
                self.errors.append(entry)
                return None


def enrich(repo, fetcher, window, discovery):
    metadata = fetcher.get("repos/" + repo)
    if metadata is None:
        return None, []
    repo = canonical_repo(metadata.get("full_name", repo))
    root = "https://github.com/" + repo
    candidate = {"repo": repo, "url": root, "title": metadata.get("name"), "description": metadata.get("description"),
                 "stars_observed": metadata.get("stargazers_count"), "retrieved_at_utc": utc_now(),
                 "discovery": discovery, "verification_status": "unverified", "claim_sources_must_be_opened": True,
                 "repository_created": classify_date(metadata.get("created_at"), window),
                 "repository_pushed": classify_date(metadata.get("pushed_at"), window),
                 "activity_is_not_launch_evidence": True, "events": [],
                 "source_urls": [root], "event": {"basis": "no_eligible_release_publication_found", "window_status": "unknown"}}
    releases = fetcher.get("repos/" + repo + "/releases?per_page=10")
    candidate["release_scan"] = {"limit": 10, "paginated": False, "status": "success" if releases is not None else "failed"}
    for release in releases or []:
        if release.get("draft"):
            continue
        event = {"basis": "github_release_published_at", **classify_date(release.get("published_at"), window),
                 "name": release.get("name") or release.get("tag_name"), "url": release.get("html_url"),
                 "prerelease": release.get("prerelease", False), "is_product_launch": "not_established"}
        candidate["events"].append(event)
        if event["url"]:
            candidate["source_urls"].append(event["url"])
    eligible = [e for e in candidate["events"] if e["date"] and not e["rejected_future"]]
    if eligible:
        candidate["event"] = max(eligible, key=lambda item: item["date"])
    readme = fetcher.get("repos/" + repo + "/readme")
    visuals = []
    if readme is not None:
        source_url = readme.get("html_url") or root + "/blob/" + metadata.get("default_branch", "main") + "/README.md"
        candidate["source_urls"].append(source_url)
        try:
            if readme.get("encoding") != "base64":
                raise ValueError("README encoding is not base64; content not parsed")
            markdown = base64.b64decode(readme["content"]).decode("utf-8", "replace")
            visuals = visual_references(markdown, repo, metadata.get("default_branch", "main"), readme.get("path", "README.md"), source_url)
            for visual in visuals:
                visual["retrieved_at_utc"] = utc_now()
        except (ValueError, KeyError) as exc:
            fetcher.errors.append({"url": source_url, "error_kind": "readme_parse", "message": str(exc), "retrieved_at_utc": utc_now()})
    candidate["window_status"] = candidate["event"]["window_status"]
    return candidate, visuals


def run(args, fetcher=None):
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    window = calendar_window(args.days, args.as_of)
    fetcher = fetcher or Fetcher(out, args.max_requests, args.retries)
    manifest = {"schema_version": 1, "started_at_utc": utc_now(), "window": window,
                "method": "GitHub activity discovery and release-metadata enrichment; agent verification required",
                "request_cap": args.max_requests, "retries_per_request": args.retries, "queries": [],
                "release_scan_limit_per_repo": 10, "media_downloaded": False}
    selected = {}
    for value in args.repo:
        selected.setdefault(canonical_repo(value), []).append({"basis": "explicit_repository"})
    if not args.repo:
        for query in args.query or DEFAULT_QUERIES:
            expression = f"{query} pushed:{window['lower_date']}..{window['upper_date']} archived:false"
            manifest["queries"].append(expression)
            endpoint = "search/repositories?" + urllib.parse.urlencode({"q": expression, "sort": "stars", "order": "desc", "per_page": args.limit})
            response = fetcher.get(endpoint)
            if response is not None:
                for item in response.get("items", []):
                    key = canonical_repo(item["full_name"])
                    selected.setdefault(key, []).append({"basis": "repository_pushed_search_not_launch", "query": expression})
    candidates, visuals = [], []
    for repo, discovery in list(selected.items())[:args.limit]:
        candidate, found = enrich(repo, fetcher, window, discovery)
        if candidate is not None:
            candidates.append(candidate)
            visuals.extend(found)
    total_failure = bool(fetcher.errors) and not candidates
    status = "total_failure" if total_failure else "partial" if fetcher.errors else "success"
    exit_code = 2 if total_failure else 1 if fetcher.errors else 0
    manifest.update(finished_at_utc=utc_now(), status=status, exit_code=exit_code, requests=fetcher.requests,
                    errors=fetcher.errors, counts={"discovered_unique": len(selected), "shortlisted": min(len(selected), args.limit),
                    "enriched": len(candidates), "visual_references": len(visuals), "request_attempts": fetcher.network_attempts,
                    "source_errors": len(fetcher.errors)})
    for filename, data in [("candidates.json", {"schema_version": 1, "window": window, "candidates": candidates}),
                           ("visual-index.json", {"schema_version": 1, "visuals": visuals}), ("run-manifest.json", manifest)]:
        (out / filename).write_text(json.dumps(data, indent=2) + "\n")
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", nargs="?", choices=["discover"], default="discover")
    parser.add_argument("--days", type=int, default=30, help="inclusive UTC calendar days, 1..366")
    parser.add_argument("--as-of", default=datetime.now(timezone.utc).date().isoformat())
    parser.add_argument("--out", required=True)
    parser.add_argument("--query", action="append", default=[], help="up to six GitHub discovery queries")
    parser.add_argument("--repo", action="append", default=[], help="OWNER/NAME; bypass search, repeatable")
    parser.add_argument("--limit", type=int, default=10, help="maximum repos enriched, 1..20")
    parser.add_argument("--max-requests", type=int, default=100, help="network attempt budget, 1..160")
    parser.add_argument("--retries", type=int, default=1, help="transient server retries, 0..2")
    args = parser.parse_args(argv)
    try:
        calendar_window(args.days, args.as_of)
        if not 1 <= args.limit <= 20 or not 1 <= args.max_requests <= 160 or not 0 <= args.retries <= 2 or len(args.query) > 6:
            raise ValueError("limit 1..20; max-requests 1..160; retries 0..2; at most six queries")
        for value in args.repo:
            canonical_repo(value)
    except ValueError as exc:
        parser.error(str(exc))
    result = run(args)
    print(json.dumps({"status": result["status"], "counts": result["counts"], "out": str(Path(args.out).resolve())}))
    return result["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
