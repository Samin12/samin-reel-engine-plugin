---
name: reel-director
description: "Coordinate Samin’s complete reel pipeline or resume a multi-stage reel job; route into the stage-specific skills and track actual readiness."
---

# Reel director

Resolve `<plugin>` as the directory containing this plugin's `.codex-plugin/`. Run `python3 <plugin>/scripts/reel.py context` to find the configured project; pass `--project /absolute/checkout` **before** `context` when a project was supplied. Treat every `production/...`, `voice/...` and `runs/...` path as relative to that project. Shared references are linked below; load only this stage's instructions. Keep credentials and large working media out of the plugin cache.

Read [operator runbook](../../references/operator-runbook.md). Inspect the existing reel state and artifacts before starting. Use `reel.py doctor` to identify missing local dependencies; it does not verify provider authentication. Do not repeat a completed batch transcription, recreate the project or overwrite a prior edit.

Route by the next unfinished outcome:

| Need | Skill |
|---|---|
| Evidence, saved stories and useful resources | `reel-research` |
| Hooks, angle and a giveaway promise | `reel-ideation` |
| Spoken copy in Samin's voice | `reel-script` |
| Download, transcription and take selection | `reel-intake` |
| Genuine screenshots, recordings and asset index | `reel-assets` |
| A missing conceptual image, clip or sound | `reel-generate` |
| Cuts, placement, captions, sound and rendering | `reel-edit` |
| Actual-render judgment and repairs | `reel-review` |
| Giveaway, Skool, ManyChat and release handoff | `reel-deliver` |

Use the current task's tools and available subagents when useful; do not require a particular model tier. Give any worker a bounded beat/stage, input files, owned output paths and pass criteria. Do not hand a smaller model the entire repository or ask it to invent the workflow. Preserve other agents' edits.

Maintain `operator-state.json`: observed stage, input/output paths, current issue, next action, exact render hash and review status. The original script/voice, source evidence, asset job, final picture and CTA must remain traceable. A valid JSON file is not proof that its claims are true.

Use the [state template](../../templates/operator-state.json) for a new job; fill real inputs before advancing its stage. Keep it in the project run, not the installed plugin.

For video requests, deliver an actual MP4, index/timeline and review receipt. For research-only requests, stop at the requested research artifact. Keep full playback, publication and subscriber delivery pending until actually observed. Creating the pipeline does not authorize unrelated messages, jobs or account changes.
