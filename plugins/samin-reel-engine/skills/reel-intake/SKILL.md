---
name: reel-intake
description: "Turn a supplied Drive filming batch into verified local media, timestamped transcripts and a complete selected take without replacing Samin’s voice."
---

# Reel filming intake

Resolve `<plugin>` as the directory containing this plugin's `.codex-plugin/`. Run `python3 <plugin>/scripts/reel.py context` to find the configured project; pass `--project /absolute/checkout` **before** `context` when a project was supplied. Treat every `production/...`, `voice/...` and `runs/...` path as relative to that project. Shared references are linked below; load only this stage's instructions. Keep credentials and large working media out of the plugin cache.

Read the Intake and command sections of [operator runbook](../../references/operator-runbook.md), then `<project>/production/intake/README.md`. Check the existing intake manifest before downloading/transcribing anything again.

List the actual supplied Drive folder, choose the intended recording, preserve Drive ID/expected bytes and use its authorized download. Verify complete size, hash, duration and decode. Keep original and audio-polished versions distinct. Never change sharing to bypass access.

Run the existing intake helper to transcribe/index, or reuse a transcript proven to belong to this source. Inspect candidate ranges for restarts, omitted intros, repeated lines and the entire final CTA. The matcher reports observed word overlap, not approved clean takes.

Save a source-relative EDL, then run the existing take helper to create continuous A-roll and retimed words. Use speed 1 unless the actual reference/performance supports another choice. Preserve word attacks, speaker meaning and natural transitions. If using a same-script reference soundtrack for calibration, explicitly map the original picture to that audio; do not reuse it for a different script.

Deliver source receipt, EDL, A-roll, word timestamps and unresolved transcription/cut issues to `reel-edit`. Do not trim the batch based solely on a transcript matcher or imply all candidate takes are approved.
