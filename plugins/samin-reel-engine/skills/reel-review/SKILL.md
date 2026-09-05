---
name: reel-review
description: "Judge the actual reel against its spoken claims and reference, inspect readability/motion/sound, and produce timecoded fixes without inventing approval."
---

# Reel quality review

Resolve `<plugin>` as the directory containing this plugin's `.codex-plugin/`. Run `python3 <plugin>/scripts/reel.py context` to find the configured project; pass `--project /absolute/checkout` **before** `context` when a project was supplied. Treat every `production/...`, `voice/...` and `runs/...` path as relative to that project. Shared references are linked below; load only this stage's instructions. Keep credentials and large working media out of the plugin cache.

Read [quality procedure](../../references/quality-procedure.md) and `<project>/production/editorial-judgment.md`. Review the actual hashed output, not just the planned timeline or previous render.

Check each beat's visible detail against the source and narration. Count entities, read product/model names, verify input/result relationships and identify irrelevant or misleading proof. Inspect source crops and captions at phone size. Watch whole playback with sound for timing, lip sync, speech clarity, cuts and final-word integrity; document tool/perception limits.

For the intro, run the quality procedure's **first-frame and two-second cold-view test** before judging action density. An unbriefed viewer must understand subject/payoff/focal detail/relationship simultaneously from the paused first frame at phone size, before seeing animation. Fail a giant number without unit/context or essential labels revealed later. Then check the first two seconds preserve the complete meaning. Save the actual still-frame answers in `opening.cold_view`; an informed self-check is not a cold test. Repair hierarchy/context, not merely cut count.

Then review opening motion at **1× phone size**. Prefer unchanged-image holds of at most about 0.5 seconds; fail holds over 1 second unless Samin changed that instruction. Tiny slow zooms, hidden/subpixel animation and captions over an inert graphic do not pass. Record first useful action, shot durations, unchanged visual spans and the brief split-to-full-screen decision in `opening.motion_cadence`. Require meaningful visible action/view changes and readable evidence together; still-frame clarity alone is insufficient.

Apply the quality procedure's mandatory music/motion checks. Hear the instrumental bed in the opening, body and CTA; missing music without Samin's explicit opt-out is a completion failure. Check beat-supported reveals and clearly audible, stronger purposeful SFX while every spoken word remains intelligible. Inspect whether the first 3–5 seconds carry the strongest useful action and variety, whether moving B-roll/full-screen inserts add useful diversity, and whether static-proof zooms preserve important details at both endpoints and during reading. Repeated motion with no new useful view is not a substitute for diversity.

Record these observations in `creative-review.json` beside the timeline, tied to the reviewed output hash. Separate recorded action, authored motion, camera moves on stills and intentional still holds. Keep counts and plans distinct from actual playback observations; a music filename or an audio stream is not evidence that the bed is audible.

Use the quality procedure's **Concrete pass/fail examples** and ordered gates: complete 1× speech/timing → source honesty/readability → opening/motion → music/SFX → whole-reel playback. Every gate gets `passed`, `failed` or `pending`, an actual observation/evidence path and any repair/recheck. Verify the pause EDL, adjacent words at each changed join, retimed cues and intact CTA. Known defects are failed; missing perceptual observations are pending. Neither can be overridden by the numerical rubric or technical metrics.

Do not accept “the source page is visible” as a review. State which required detail can actually be read/recognized and how it explains the spoken action. Reject noun-only source matches, generic title/question cards replacing useful visuals, unreadable full-page inserts, and caption styling that visibly diverges from the reference. Save a timecoded frame for each failure before returning it for repair.

Clearly sourced editorial collages and stat graphics need no automatic “illustration” badge. Require explicit reconstruction/illustration labels when an authored visual could be mistaken for a live UI or generated/executed result; reject false execution claims without adding unnecessary production labels to obvious graphics.

Use the synchronized review builder for aligned same-script versions. Optional scene/attention analysis is a second opinion, not automatic passage: verify its claims against actual frames. Council's scene analyzer incorrectly counted five characters where four were visible; that finding was rejected after direct inspection.

Score semantic fit, evidence honesty, timing/readability, composition/focus, and reference/voice coherence only from observations. Default pass requires 16/20, every dimension at least 3, no hard failures and actual full-render review. Technical checks, stills, ASR and predictive scores cannot replace the required observations. Leave unobserved fields pending.

Write exact timecodes, observed issue, one repair and the recheck result. Hand bounded fixes back to `reel-edit`; recheck changed beats and neighbors, then update the hash and run the mechanical editorial checker. Deliver a review candidate clearly when full perceptual review remains unavailable; do not certify it to end the task.
