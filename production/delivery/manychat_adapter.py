#!/usr/bin/env python3
"""Read ManyChat automation metadata or prepare a local publication handoff.

Default command is an offline dry run. This adapter has no sending or mutation
implementation. ManyChat's current public API does not expose flow authoring.
"""
import argparse
import ipaddress
import json
import os
from pathlib import Path
import stat
import sys
import urllib.error
import urllib.parse
import urllib.request

API_ORIGIN = "https://api.manychat.com"
READ_PATHS = ("/fb/page/getFlows", "/fb/page/getGrowthTools")


class AdapterError(Exception):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        # Never forward credentials to a redirect destination.
        return None


def read_secret(key_file=None):
    if key_file:
        path = Path(key_file).expanduser()
        info = path.stat()
        if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) != 0o600:
            raise AdapterError("Key file must be a regular file with mode 0600.")
        if hasattr(os, "getuid") and info.st_uid != os.getuid():
            raise AdapterError("Key file must belong to the current user.")
        secret = path.read_text().strip()
    else:
        secret = os.environ.get("MANYCHAT_API_KEY", "").strip()
    if not secret or "\n" in secret or "\r" in secret:
        raise AdapterError("Supply MANYCHAT_API_KEY or an owner-only --key-file.")
    return secret


def get_metadata(path, secret):
    if path not in READ_PATHS:
        raise AdapterError("Only the two approved metadata GET endpoints are supported.")
    request = urllib.request.Request(
        API_ORIGIN + path, method="GET",
        headers={"Authorization": "Bearer " + secret, "Accept": "application/json"},
    )
    try:
        with urllib.request.build_opener(NoRedirect).open(request, timeout=25) as response:
            data = json.load(response)
    except urllib.error.HTTPError as error:
        raise AdapterError(f"ManyChat returned HTTP {error.code}; response body withheld.") from None
    except (urllib.error.URLError, ValueError, OSError):
        raise AdapterError("ManyChat metadata request failed; raw error withheld.") from None
    if not isinstance(data, dict) or data.get("status") != "success":
        raise AdapterError("ManyChat did not return success; raw response withheld.")
    return data.get("data")


def inspect(live_read=False, key_file=None, keyword="POLISH"):
    plan = {
        "mode": "read_only" if live_read else "dry_run",
        "api_origin": API_ORIGIN,
        "requests": [{"method": "GET", "path": p} for p in READ_PATHS],
        "matching_rule": "Case-insensitive metadata name match only; not trigger or content search.",
        "keyword": keyword,
        "mutation_supported": False,
        "subscriber_access": False,
    }
    if not live_read:
        plan["network_requests_performed"] = 0
        plan["secret_loaded"] = False
        return plan
    secret = read_secret(key_file)
    counts, matches = {}, {}
    for path in READ_PATHS:
        data = get_metadata(path, secret)
        rows = data.get("flows", []) if isinstance(data, dict) else data
        if not isinstance(rows, list) or not all(isinstance(x, dict) for x in rows):
            raise AdapterError("Unexpected metadata schema; no raw output emitted.")
        label = path.rsplit("/", 1)[-1]
        allowed = ("ns", "name", "folder_id") if label == "getFlows" else ("id", "name", "type")
        counts[label] = len(rows)
        matches[label] = [
            {k: row.get(k) for k in allowed}
            for row in rows if keyword.casefold() in str(row.get("name", "")).casefold()
        ]
    plan.update(counts=counts, matching_metadata=matches, network_requests_performed=2)
    plan["content_availability"] = "Exact messages, destination links, keyword configuration and post mapping are not returned. Inspect the app."
    return plan


def public_https(value, instagram=False):
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        u = urllib.parse.urlsplit(value)
        host = (u.hostname or "").lower()
        if u.scheme != "https" or u.username or u.password or not host or u.port not in (None, 443):
            return False
        if host == "localhost" or host.endswith((".local", ".test", ".invalid", ".example")) or host in {"example.com", "example.org", "example.net"}:
            return False
        try:
            if not ipaddress.ip_address(host).is_global:
                return False
        except ValueError:
            pass
        if instagram and (host not in {"instagram.com", "www.instagram.com"} or not u.path.startswith(("/p/", "/reel/"))):
            return False
        return True
    except ValueError:
        return False


def prepare(handoff, reel_id, asset_url=None, post_url=None):
    data = json.loads(Path(handoff).read_text())
    candidates = data.get("reels", []) if isinstance(data, dict) else []
    matches = [r for r in candidates if r.get("reel_id") == reel_id]
    if len(matches) != 1:
        raise AdapterError("Select one existing reel_id from the handoff.")
    reel = matches[0]
    asset = asset_url or reel.get("asset_url")
    post = post_url or reel.get("post_id_or_url")
    opening = reel.get("opening_dm", {})
    delivery = reel.get("delivery_dm", {})
    quick = opening.get("quick_reply", {})
    blockers = []
    if not public_https(asset):
        blockers.append("A real public HTTPS resource URL is required.")
    if not public_https(post, instagram=True):
        blockers.append("Select the corresponding published Instagram post/reel URL.")
    if not reel.get("keyword"):
        blockers.append("Missing exact comment keyword.")
    if reel.get("trigger", {}).get("scope") != "specific_reel":
        blockers.append("New publication packet must select its specific reel.")
    if not (opening.get("enabled") and opening.get("send_as_private_reply") and opening.get("content_blocks") == 1 and opening.get("text")):
        blockers.append("Opening private reply must contain one text block.")
    if not quick.get("label") or quick.get("action") != "send_message" or quick.get("target") != "delivery_dm":
        blockers.append("Opening quick reply must lead to the delivery message.")
    if opening.get("automatic_next_step") or opening.get("website_button"):
        blockers.append("Do not bypass the opening interaction with an automatic step or website button.")
    if delivery.get("send_only_after") != "opening_dm.quick_reply interaction" or not delivery.get("text"):
        blockers.append("Delivery must wait for the opening quick-reply interaction.")
    if reel.get("optional_reminder", {}).get("enabled"):
        blockers.append("Reminder requires separate review; keep it disabled in this adapter.")
    return {
        "schema_kind": "local_manychat_ui_publication_packet",
        "direct_import_compatible": False,
        "mode": "dry_run",
        "reel_id": reel_id,
        "automation_name": reel.get("automation_name"),
        "keyword": reel.get("keyword"),
        "specific_post_url": post,
        "asset_url": asset,
        "public_replies": reel.get("public_replies", []),
        "opening_dm": opening,
        "delivery_dm": {**delivery, "button": {**delivery.get("button", {}), "url": asset}},
        "optional_reminder": {"enabled": False},
        "input_blockers": blockers,
        "status": "inputs_incomplete" if blockers else "ready_for_authorized_ui_configuration",
        "remaining_live_steps": [
            "Confirm resource opens for the intended free/paid/community audience.",
            "Inspect duplicate keyword triggers and match the correct Instagram account.",
            "Configure the specific reel and messages in ManyChat after publication is authorized.",
            "Review the exact flow, activate when authorized, then verify an authorized end-to-end test.",
            "Record the actual automation URL, reel URL, resource URL and test evidence.",
        ],
        "api_create_flow_supported": False,
        "network_requests_performed": 0,
        "external_changes_performed": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command")
    read = sub.add_parser("inspect", help="Offline plan by default; optional live metadata reads")
    read.add_argument("--live-read", action="store_true")
    read.add_argument("--key-file")
    read.add_argument("--keyword", default="POLISH")
    build = sub.add_parser("prepare", help="Build a local UI handoff; never sends or creates flows")
    build.add_argument("--handoff", required=True)
    build.add_argument("--reel-id", required=True)
    build.add_argument("--asset-url")
    build.add_argument("--post-url")
    build.add_argument("--output")
    args = p.parse_args()
    try:
        if args.command == "prepare":
            result = prepare(args.handoff, args.reel_id, args.asset_url, args.post_url)
        else:
            result = inspect(getattr(args, "live_read", False), getattr(args, "key_file", None), getattr(args, "keyword", "POLISH"))
        text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        if getattr(args, "output", None):
            Path(args.output).write_text(text)
        else:
            print(text, end="")
    except (AdapterError, OSError, ValueError):
        # Avoid echoing arbitrary input, exception data, headers or secrets.
        print("Adapter failed validation or read. Check inputs, key-file permissions and official API availability; raw diagnostics withheld.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
