#!/usr/bin/env python3
"""Count clean spoken scripts; optionally delimit a script with SCRIPT START/END comments."""
import argparse
import json
import re
from pathlib import Path


def measure(text, slow_wpm=150, fast_wpm=180):
    text = re.sub(r"\A---\s*\n.*?\n---\s*\n", "", text, flags=re.S)
    if "<!-- SCRIPT START -->" in text:
        if "<!-- SCRIPT END -->" not in text:
            raise ValueError("Missing SCRIPT END marker")
        text = text.split("<!-- SCRIPT START -->", 1)[1].split("<!-- SCRIPT END -->", 1)[0]
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if any(line.startswith(("#", "|", "```")) for line in lines):
        raise ValueError("Use a clean spoken script or SCRIPT START/END markers; editorial text affects timing")
    words = len(text.split())
    beats = len(lines)
    return {
        "words": words,
        "spoken_beats": beats,
        "hook_words": len(lines[0].split()) if lines else 0,
        "estimated_seconds": {"fast": round(words / fast_wpm * 60, 1), "slow": round(words / slow_wpm * 60, 1)},
        "assumed_wpm": {"slow": slow_wpm, "fast": fast_wpm},
        "inside_standard_corpus_word_range": 98 <= words <= 195,
        "inside_standard_corpus_beat_range": 7 <= beats <= 12,
        "last_line": lines[-1] if lines else "",
        "note": "Planning estimate, not a measured recording or a voice-match score.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--slow-wpm", type=int, default=150)
    parser.add_argument("--fast-wpm", type=int, default=180)
    args = parser.parse_args()
    if not 0 < args.slow_wpm <= args.fast_wpm:
        parser.error("Need 0 < slow-wpm <= fast-wpm")
    results = []
    for path in args.paths:
        try:
            results.append({"file": path, **measure(Path(path).read_text(), args.slow_wpm, args.fast_wpm)})
        except (OSError, ValueError) as exc:
            parser.error(f"{path}: {exc}")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
