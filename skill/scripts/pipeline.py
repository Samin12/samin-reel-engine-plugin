#!/usr/bin/env python3
"""File-based reel pipeline checker. init creates empty scaffolds, never content.

Usage: python3 pipeline.py {init,status,validate} --run PATH
status/init exit 0; validate exits 1 until all four draft stages are ready.
Draft readiness is structural completeness, not editorial or deployment approval.
"""
import argparse
import ipaddress
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlsplit


def timestamp():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def item_id(item):
    return item.get("id") or item.get("reel_id") or item.get("idea_id") or item.get("story_id")


def keyword(item):
    return str(item.get("keyword") or "").strip().upper()


def read_rows(run, name, key, issues):
    path = run / name
    if not path.is_file():
        issues.append(f"missing {name}")
        return []
    try:
        data = json.loads(path.read_text())
        rows = data if isinstance(data, list) else data.get(key)
        if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
            raise ValueError(f"expected an array of objects in {key}")
        if not rows:
            issues.append(f"{name}: no {key} yet")
        return rows
    except (OSError, ValueError, AttributeError) as exc:
        issues.append(f"{name}: {exc}")
        return []


def index_rows(rows, label, issues):
    indexed = {}
    for row in rows:
        ident = item_id(row)
        if not isinstance(ident, str) or not ident.strip():
            issues.append(f"{label}: missing ID")
        elif ident in indexed:
            issues.append(f"{label}: duplicate ID {ident}")
        else:
            indexed[ident] = row
    return indexed


def local_file(run, value, folder):
    if not isinstance(value, str) or not value.strip():
        return None, f"missing {folder} file path"
    path = Path(value)
    if not path.is_absolute():
        # Older manifests stored paths relative to the package, not the run.
        if value.startswith(f"runs/{run.name}/") and run.parent.name == "runs":
            path = run.parent.parent / path
        else:
            path = run / path
    path = path.resolve()
    if not path.is_relative_to((run / folder).resolve()):
        return None, f"{folder} path must stay inside this run: {value}"
    try:
        if not path.is_file() or path.stat().st_size == 0:
            return None, f"{folder} file missing or empty: {value}"
    except OSError as exc:
        return None, f"cannot inspect {value}: {exc}"
    return path, None


def public_https(value):
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        parsed = urlsplit(value)
        host = parsed.hostname or ""
        if parsed.scheme != "https" or not host or parsed.username or parsed.password:
            return False
        if host in {"example.com", "example.org", "example.net", "localhost"} or host.endswith((".example.com", ".example.org", ".example.net", ".localhost", ".test", ".invalid", ".local", ".example")):
            return False
        if any(token in host for token in ("placeholder", "yourdomain", "your-domain")) or "." not in host:
            return False
        if re.search(r"[<>{}]|\b(?:TODO|REPLACE_ME|INSERT_URL|PLACEHOLDER|REEL_ID|POST_ID|YOUR_REEL|YOUR_POST)\b", unquote(value), re.I):
            return False
        try:
            return ipaddress.ip_address(host).is_global
        except ValueError:
            return True
    except ValueError:
        return False


def post_reference(value):
    if isinstance(value, str) and re.fullmatch(r"[0-9]{5,}", value):
        return True
    if not public_https(value):
        return False
    parsed = urlsplit(value)
    return parsed.hostname in {"instagram.com", "www.instagram.com"} and bool(re.fullmatch(r"/(?:reel|p)/[A-Za-z0-9_-]{5,}/?", parsed.path))


def stage(run, file, issues, count):
    return {"status": "missing" if not (run / file).is_file() else "needs_work" if issues else "ready",
            "count": count, "blockers": issues}


def inspect(run):
    run = Path(run).resolve()
    research_issues, idea_issues, script_issues, asset_issues = [], [], [], []
    stories = read_rows(run, "research/story-bank.json", "stories", research_issues)
    story_map = index_rows(stories, "stories", research_issues)
    for ident, row in story_map.items():
        if not row.get("title") or not isinstance(row.get("sources"), list) or not row["sources"]:
            research_issues.append(f"story {ident}: title and source list required")
    research = stage(run, "research/story-bank.json", research_issues, len(story_map))

    ideas = read_rows(run, "ideation/ideas.json", "ideas", idea_issues)
    idea_map = index_rows(ideas, "ideas", idea_issues)
    selected = {ident: row for ident, row in idea_map.items() if row.get("selected") is True or row.get("decision") == "selected"}
    if not selected:
        idea_issues.append("no selected ideas")
    if research["status"] != "ready":
        idea_issues.append("dependency research is not ready")
    for ident, row in selected.items():
        refs = row.get("story_ids") or [row.get("story_id")]
        if not isinstance(refs, list) or not refs or any(not isinstance(ref, str) or ref not in story_map for ref in refs):
            idea_issues.append(f"idea {ident}: missing or stale story reference")
        if not keyword(row):
            idea_issues.append(f"idea {ident}: keyword required")
    ideation = stage(run, "ideation/ideas.json", idea_issues, len(selected))

    reels = read_rows(run, "reel-manifest.json", "reels", script_issues)
    reel_map = index_rows(reels, "reels", script_issues)
    if ideation["status"] != "ready":
        script_issues.append("dependency ideation is not ready")
    keywords, referenced_ideas, assets = {}, set(), {}
    for ident, reel in reel_map.items():
        idea_id = reel.get("idea_id")
        if idea_id not in selected:
            script_issues.append(f"reel {ident}: idea_id must reference a selected idea")
        else:
            referenced_ideas.add(idea_id)
            if keyword(reel) != keyword(selected[idea_id]):
                script_issues.append(f"reel {ident}: keyword differs from selected idea")
        word = keyword(reel)
        if not word:
            script_issues.append(f"reel {ident}: keyword required")
        elif word in keywords:
            script_issues.append(f"duplicate keyword {word}: {keywords[word]} and {ident}")
        keywords[word] = ident
        script, error = local_file(run, reel.get("script_path") or reel.get("script"), "scripts")
        if error:
            script_issues.append(f"reel {ident}: {error}")
        elif word and not re.search(r"\bcomment\s+" + re.escape(word) + r"\b", script.read_text(errors="replace").replace("*", ""), re.I):
            script_issues.append(f"reel {ident}: script lacks matching Comment {word} CTA")
        asset, error = local_file(run, reel.get("asset_path") or reel.get("resource"), "assets")
        if error:
            asset_issues.append(f"reel {ident}: {error}")
        else:
            assets[ident] = asset
            planned = selected.get(idea_id, {}).get("giveaway") or {}
            if isinstance(planned, dict) and planned.get("path"):
                planned_asset, _ = local_file(run, planned["path"], "assets")
                if planned_asset != asset:
                    asset_issues.append(f"reel {ident}: giveaway file differs from selected idea")
    for ident in selected.keys() - referenced_ideas:
        script_issues.append(f"selected idea {ident}: no reel script in manifest")
    scripting = stage(run, "reel-manifest.json", script_issues, len(reel_map))

    packets = read_rows(run, "manychat/handoff.json", "reels", asset_issues)
    packet_map = index_rows(packets, "handoff packets", asset_issues)
    if scripting["status"] != "ready":
        asset_issues.append("dependency scripting is not ready")
    deployment = {}
    for ident, reel in reel_map.items():
        packet = packet_map.get(ident)
        blocked = []
        if packet is None:
            asset_issues.append(f"reel {ident}: missing ManyChat handoff packet")
            blocked.append("missing handoff packet")
        else:
            if keyword(packet) != keyword(reel):
                asset_issues.append(f"reel {ident}: handoff keyword does not match")
            asset, error = local_file(run, packet.get("asset_path"), "assets")
            if error or asset != assets.get(ident):
                asset_issues.append(f"reel {ident}: handoff asset must match the real giveaway file")
            if not isinstance(packet.get("message_text"), str) or not packet["message_text"].strip():
                asset_issues.append(f"reel {ident}: delivery message_text required")
            if not public_https(packet.get("asset_url")):
                blocked.append("missing real public HTTPS asset_url")
            if not post_reference(packet.get("post_id_or_url")):
                blocked.append("missing actual Instagram reel/post ID or URL")
            test = packet.get("live_test") or {}
            if not isinstance(test, dict) or test.get("status") != "passed" or not test.get("tested_at_utc") or not test.get("evidence"):
                blocked.append("live delivery test with timestamp and evidence has not passed")
        deployment[ident] = {"ready": not blocked, "blockers": blocked}
    for ident in packet_map.keys() - reel_map.keys():
        asset_issues.append(f"handoff packet {ident}: no matching reel")
    giveaway = stage(run, "manychat/handoff.json", asset_issues, len(assets))
    stages = {"research": research, "ideation": ideation, "scripting": scripting, "giveaway_assets": giveaway}
    draft_ready = all(value["status"] == "ready" for value in stages.values())
    if not draft_ready:
        for result in deployment.values():
            result["ready"] = False
            result["blockers"].append("draft pipeline stages are incomplete")
    blockers = [] if draft_ready else ["draft pipeline stages are incomplete"]
    blockers += [f"{ident}: {reason}" for ident, result in deployment.items() for reason in result["blockers"]]
    result = {"schema_version": 1, "checked_at_utc": timestamp(), "run": str(run), "stages": stages,
              "draft_ready": draft_ready, "deployment_ready": draft_ready and bool(deployment) and not blockers,
              "deployment_blockers": blockers, "deployment_by_reel": deployment,
              "readiness_basis": "Local file structure and recorded handoff evidence; no publishing, live verification, or AI writing executed."}
    run.mkdir(parents=True, exist_ok=True)
    (run / "pipeline-status.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def initialize(run):
    run = Path(run).resolve()
    for folder in ("research", "ideation", "scripts", "assets", "manychat"):
        (run / folder).mkdir(parents=True, exist_ok=True)
    for name, key in [("research/story-bank.json", "stories"), ("ideation/ideas.json", "ideas"),
                      ("reel-manifest.json", "reels"), ("manychat/handoff.json", "reels")]:
        path = run / name
        if not path.exists():
            path.write_text(json.dumps({"schema_version": 1, key: []}, indent=2) + "\n")
    return inspect(run)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["init", "status", "validate"])
    parser.add_argument("--run", required=True)
    args = parser.parse_args(argv)
    result = initialize(args.run) if args.command == "init" else inspect(args.run)
    print(json.dumps(result, indent=2))
    return 1 if args.command == "validate" and not result["draft_ready"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
