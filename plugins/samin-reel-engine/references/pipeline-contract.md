# Pipeline contract

One run lives under `<project>/runs/YYYY-MM-DD/`; use a suffix for another batch the same day. Preserve the existing run when resuming. The script helpers are local tools, while the assistant supplies the research and writing judgment.

## Research

Write `research/story-bank.json` with a `stories` list containing stable `id` values and the evidence fields in `research-contract.md`. Preserve rejected candidates and raw evidence separately. Save `research/visual-index.json`. A fresh repository push is a discovery signal, not a product launch.

Start with Eden and write `research/saved-resources.json` using `saved-resources.md`: access status, search scope, inspected item IDs/URLs, original URLs, date evidence, content-read status, short summaries, verification and reuse decisions. Record an explicit access limitation if needed. Keep this source of ideas separate from the fresh-news date window.

## Ideation

Write `ideation/ideas.json`:

```json
{"ideas":[{"id":"idea-story-001","story_id":"story-001","selected":true,"archetype":"new-tool","angle":"Specific viewer payoff","hook_options":["Hook one","Hook two","Hook three"],"selected_hook":"Hook one","keyword":"WORD","giveaway":{"title":"Useful checklist","path":"assets/WORD.md","promise":"the connection checklist"},"script_path":"scripts/01-WORD.md"}]}
```

Also write a readable `ideas.md` with the recommendation and reasoning. Hooks remain alternatives here; the script gets one selected opening. Giveaways are designed during ideation, then built from the final script.

Add `saved_resource_ids` to the idea/giveaway when an inspected bookmark contributes to it. An empty list means no relevant saved resource was incorporated; it must not be presented as Eden-derived.

## Scripting

Write clean spoken text in `scripts/`. `reel-manifest.json` is a list of records linking `id`, `idea_id`, `keyword`, `script_path`, `asset_path`, voice-sample anchors and checks. Paths are relative to the run; older package-relative `script`/`resource` fields may coexist for compatibility. Keep facts traceable to the selected story.

## Giveaway assets

Write each promised resource under `assets/` and create `manychat/handoff.json` plus `manychat/SETUP.md` using `manychat.md`. The handoff joins each reel, keyword, final asset and message copy. Keyword changes must propagate to the idea, script, manifest, asset and handoff together.

Also write `skool/drafts/<KEYWORD>.md` and `skool/handoff.json` using `skool.md`. Verify that every selected reel has the correct resource, hash, source attribution and post draft. An extra community resource may be marked `bonus_resource` with no reel ID; it does not become a ManyChat automation unless a matching reel/promise is added. The current helper does not validate these Skool fields, so inspect them explicitly in the run receipt.

`pipeline.py status --run <run>` writes `pipeline-status.json` with stage readiness and deployment blockers. `validate` is useful before handing off a batch. These are integrity checks, not proof of writing quality or a live integration.

## Distribution is a distinct state

`draft_ready` means a local resource and complete setup copy exist. `deployment_ready` also needs a real public HTTPS asset URL, an assigned post/reel, and a confirmed delivery test. Missing hosting or account access must remain explicit. A completed local pipeline never means the automation has been activated.

After the user accepts a revision, preserve the before/after files, synchronize the script and its promise, and record acceptance in the story ledger. Publication needs its own observed event; do not infer it from an accepted draft.
