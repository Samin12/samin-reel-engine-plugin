---
name: reel-edit
description: "Edit Samin’s original footage into a music-backed reel with moving evidence B-roll, an active opening, short captions, audible SFX and a real HyperFrames MP4 export."
---

# Reel editing

Resolve `<plugin>` as the directory containing this plugin's `.codex-plugin/`. Run `python3 <plugin>/scripts/reel.py context` to find the configured project; pass `--project /absolute/checkout` **before** `context` when a project was supplied. Treat every `production/...`, `voice/...` and `runs/...` path as relative to that project. Shared references are linked below; load only this stage's instructions. Keep credentials and large working media out of the plugin cache.

Read [operator runbook](../../references/operator-runbook.md), [shot recipes](../../references/shot-recipes.md), and `<project>/production/editor/README.md`. Use the existing renderer; do not rebuild it or substitute an avatar. The Council v2 pilot is a measured example, not a timeline to copy into a different script.

Execute the runbook's **Repeatable order for a filmed reel**: preserve inputs → finish speech/EDL and retime → acquire opening/music → export and inspect the opening with sound → complete/render → review/repair. Each step names the artifact that proves it happened. Use the quality procedure's concrete pass/fail examples when a choice is unclear; do not infer success from a filename, plan or successful encode.

Run the reference-calibration step before choosing treatments. Inspect an existing supplied style reference's concrete actions/metaphors and measured profile; a matching finished edit of the new script is not required. Apply the recorded house style and Samin's current feedback when there is no new reference. Real evidence still needs a clear focal detail; a reel filled with static text diagrams does not match the house style merely because the captions are correct.

Tighten verified intra-sentence pauses as well as failed takes using the runbook's waveform/word-boundary and frame-aligned EDL procedure. Preserve the actual words and natural joins; retime all dependent cues after any speech cut. Lock the edited voice/words and create the editorial map. For every beat, assign a viewer question, proof/explanation/metaphor/presenter job, asset, spoken anchor, reveal and stable reading hold. Use full-screen evidence when half-screen would be unreadable. Keep required source context, face and captions clear.

After `prepare_take.py`, use `reel.py --project /absolute/checkout run retime -- --spec OLD --cuts REMOVALS --source NEW_AROLL --words NEW_WORDS --output NEW_TIMELINE` for an existing edit; see the runbook for the exact command and removal-list contract on the **old output clock**. It remaps supported outer cues and preserves caption word indices. Remove/replan any old music configuration around this step and add a continuous bed afterward. Manually recheck actions inside B-roll and SFX tails: the helper does not retime those contents or certify sync.

**Samin requires instrumental background music unless he explicitly opts out for this reel.** Obtain and index a playable track, map beats/energy to the locked voice, and keep the bed audible through the body/CTA with a clean ending. A provider failure or another audio skill's optional-music rule does not waive this requirement. Use the asset playbook's fallback; never silently ship voice plus SFX as the completed edit.

Put the highest useful action and visual diversity in the **first 3–5 seconds**. Prefer real moving B-roll and use it full-screen freely when it improves impact or clarity. Vary source types, views, details and shot scales. Normally give static proof a slow directed zoom/reframe while preserving key words and context; inspect both endpoints and the reading hold. Make intro accents and useful action SFX clearly audible, stronger than the first Mobbin pilot, while keeping all speech intelligible. See the shot recipes for mix starting points and motion treatments.

Make the **whole graphic hook clear simultaneously in one paused first frame**: dominant subject, specific payoff, supporting detail and relationship. Keep that meaning visible through the opening. A large result/count needs its unit and subject/context already present; ordered animation must not supply essential labels later. Before motion polish, run the quality procedure's unbriefed phone-size still-frame test, then verify the first two seconds preserve comprehension. Motion reinforces the idea; extra cuts cannot repair ambiguity.

The opening must also move visibly at scrolling speed: prefer **≤0.5 seconds unchanged**, with **1 second maximum** per unchanged intro image unless Samin says otherwise. A tiny slow zoom or changing captions over an inert graphic is insufficient. Consider the complete graphic above Samin for roughly 0.5 seconds, then active full-screen B-roll; choose relevant source actions/details, not arbitrary cuts. Keep text readable. Record first action, shot/unchanged durations, split decision and actual 1× checks in `opening.motion_cadence`.

The [worked README beat](../../examples/council-readme-beat.json) shows one real decision. It is an excerpt, not a complete map; build the current map against the project's schema and actual word timings.

Build the timeline with actual asset paths and measured source offsets/crops. Set `audio_policy.music_required: true`, add the actual `music` track/envelope using the editor README contract, and build through `reel.py run build -- --spec TIMELINE --project COMPOSITION`; the plugin rejects missing music unless an explicit user opt-out is recorded in `audio_policy.user_opt_out`. Group captions by spoken meaning, preserve complete names/negations, and use the reference's short white/lilac phrases and softer connectors. Align selected reveals and SFX to meaningful musical accents without breaking their spoken anchors. A full same-script calibration soundtrack already contains its music/SFX; verify those layers before adding anything and do not duplicate them.

Load the reference caption preset from the shot recipes explicitly; renderer defaults are not the house style. Before a full render, compare one presenter frame and one B-roll frame against the supplied reference at equal display size. Reject opaque caption plates, oversized paragraph captions, whole-page letterboxing with tiny focal text, and generic title/question cards used in place of concrete B-roll. Make the visual do explanatory work beyond repeating the spoken words.

Build, run HyperFrames checks, inspect snapshots, then render the actual video and finalize its audio on a new path. Review encoded frames after layering/crop changes; passing browser checks once hid a blank B-roll layer. Preserve source files while the renderer uses hardlinks.

Send the actual MP4, timeline, words, EDL, asset index, `creative-review.json` and current hash to `reel-review`. The sidecar records music/beat plan, opening action, motion treatments and actual listening/crop observations; its fields are in the quality procedure. Technical render success is not editorial approval. Do not publish or send subscriber messages as part of editing.
