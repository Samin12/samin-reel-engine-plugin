---
name: reel-generate
description: "Generate only missing explanatory reel images, motion clips or effects; preserve consistency and verify results before editing them into filmed footage."
---

# Reel generation

Resolve `<plugin>` as the directory containing this plugin's `.codex-plugin/`. Run `python3 <plugin>/scripts/reel.py context` to find the configured project; pass `--project /absolute/checkout` **before** `context` when a project was supplied. Treat every `production/...`, `voice/...` and `runs/...` path as relative to that project. Shared references are linked below; load only this stage's instructions. Keep credentials and large working media out of the plugin cache.

Read [generation recipes](../../references/generation-recipes.md) and the current installed provider skill/schema. Require a specific visual job and planned slot from `reel-assets` or the user; do not generate a generic reel or replace Samin's filmed performance.

Choose static authored graphics for exact labels/counts, an image model for a visual metaphor, and image-to-video when a short action adds meaning. Keep the approved still/reference, palette and entities consistent. Request one clear action with no competing captions or fake app output. Match the intended top-split/full-screen crop.

Use the available tool/CLI according to its own media-upload contract. Preserve prompt, model/params, input hashes, returned job ID, actual output URL, local output hash and selected trim. Check existing job status after a timeout before resubmitting. Never report a queued job as finished media.

Inspect the exact usable interval for count changes, morphs, unintended text, framing, cuts and audio. Generated B-roll is muted under Samin's original voice unless a separately reviewed audio component is intentionally selected. A successful provider response is not a visual pass.

After two concrete revisions fail, simplify to an authored explanation or presenter and record why. Do not invent product screenshots, tweets, benchmark results or testimonials. Mark illustrations and provenance honestly. Hand usable indexed files plus limits to `reel-edit`.
