# Operator runbook: finish one reel without inventing the process

Use this when editing Samin's supplied footage, especially with a smaller model. Work one reel and one stage at a time. Reuse the renderer, schemas and measured examples; do not rebuild an editing framework. The goal is a reviewable video with useful visuals, not a document describing a hypothetical video.

## Resolve the job

In the plugin, run `python3 <plugin>/scripts/reel.py context`; it resolves the explicit project, `SAMIN_REEL_PROJECT`, local configuration or source checkout. Use `python3 <plugin>/scripts/reel.py --project /absolute/checkout configure` to bind a known checkout. The single-skill compatibility version instead reads `project-location.json`: use its `project_root`, or resolve `..` from the skill directory in a checkout. All `production/...` paths below are relative to the project, not this references folder or the installed plugin cache.

Collect from the existing conversation/files: reel ID, source recording or Drive folder, spoken script or transcript, reference reel, giveaway promise, current stage, and permitted destinations. Reuse already supplied inputs. Ask only for a missing input that prevents the next action. A missing optional preference is not a reason to stop.

Use a new `production/pilots/<reel-id>/` for metadata, `work/<reel-id>/` for originals/intermediates, and `outputs/` for final deliverables. Large media stays outside Git except intentional small reusable B-roll. Preserve prior renders and user edits. Do not copy Council's script, timestamps, reference soundtrack or giveaway into a different story.

Maintain one `operator-state.json` with `reel_id`, `stage`, `input_paths`, `completed_artifacts`, `current_issue`, `next_action`, `render_sha256`, and `review_status`. Store only observed state. A path, generation ID or queued job is not a finished asset. Update this record when a stage finishes so another model can resume without rediscovery.

Samin's creative defaults are **audible instrumental background music, clear stronger SFX, the highest useful action/visual variety in the first 3–5 seconds, and motion-rich real B-roll**. Prefer relevant moving footage and use it full-screen freely. Give static proof a slow purposeful zoom/reframe when its important details remain readable. These defaults apply even when there is no matching finished example. An unrelated tool's optional-music guidance does not waive Samin's requirement; only his explicit opt-out for the reel does. Record the music, opening beat plan, motion treatments and actual review observations in `creative-review.json` using [quality procedure](quality-procedure.md).

## Repeatable order for a filmed reel

Use this short execution checklist when resuming with limited context. Each checked item needs its named artifact; do not substitute a prose promise.

1. **Resolve and preserve.** Read `operator-state.json`, locate the selected master/take, verify its identity and create a new revision directory. Save the source and current-render hashes. Read only the selected script, house-style notes and current failure.
2. **Finish speech first.** Inspect false starts and small intra-sentence pauses using the waveform and real words. Save the frame-aligned keep EDL, cut reasons, complete 1× A-roll and retimed word list. Review changed joins, then the entire selected speech including the CTA. A gap proposed by ASR is not an approved edit. If speech changes later, return here and regenerate all dependent timings.
3. **Acquire the opening and sound early.** Write the subject and specific payoff in one sentence. Make the whole hook simultaneously clear in the first frame, then plan useful visible changes across the first 3–5 seconds: about 0.5 seconds per unchanged image is preferred, 1 second is the maximum. Consider Samin below/clear graphic above for roughly 0.5 seconds before active full-screen B-roll. Record the split choice, first useful action and source-view changes; tiny slow zooms alone are insufficient. Obtain actual music/visual files and name source bounds, spoken anchors, musical accents and SFX onsets before polishing.
4. **Build a short opening check.** Export the opening. Run the muted, unbriefed phone-size test on the first paused frame, then play the opening at normal speed. Confirm simultaneous clarity survives and actual action is visible; record shot lengths, unchanged-image spans and first-action timing in `opening.motion_cadence`. Repair holds over 1 second and any subpixel/hidden-only movement. Keep text readable while moving/changing useful B-roll. Inspect/listen with voice, music, SFX and captions afterward; save both observations because the muted test does not satisfy sound review.
5. **Complete and render.** Apply the same beat-to-visual method to the body and actual giveaway. Vary relevant actions/views and use full-screen motion where useful. Build, check, render and finalize on a new path. Record the real output hash and run the complete review below.
6. **Return only an accurately labelled result.** Complete `creative-review.json` and the editorial review, repair failed spans and neighbors, then re-export/recheck. Deliver `passed` only when the required observations actually pass; otherwise deliver a clearly labelled review candidate with specific `failed` or `pending` items. Missing music, damaged speech or unreadable/misleading proof cannot be hidden by a score or a successful encode.

The command shapes below and linked playbooks implement these steps. The [quality procedure's pass/fail examples](quality-procedure.md#concrete-passfail-examples) show exactly what each observation must establish. This checklist is executable guidance for any operator; it does not claim that a model which cannot perceive audio/video can certify those observations.

## Execute the stages

| Stage | Read now | Do | Observable exit |
|---|---|---|---|
| Research/voice, if no filmed script | [pipeline operations](pipeline-operations.md), voice guide and three fitting samples | Eden saves → primary sources → ideas → clean script → real giveaway; collect visuals while researching | Draft and resource exist, facts have sources, shot requests have reasons |
| Intake | `production/intake/README.md` | Download complete selected recording, verify bytes/hash, transcribe/index, inspect take and CTA | Correct source and complete selected performance are identified |
| Select/edit speech | `production/prepare_take.py --help` and existing pilot EDL | Remove false starts and repeated lines; preserve the speaker's claim; retime words | Edited A-roll and words refer to the same source/timebase |
| Calibrate the reference | Existing measured reference profile and selected reference frames; see below | Compare presenter, metaphor, screen/typing and caption treatments | Record a concrete visual target and unacceptable deviations before sourcing |
| Visual plan | [asset playbook](asset-playbook.md) and [shot recipes](shot-recipes.md) | Map every spoken beat, plan the strongest opening action/variety and musical accents | No unassigned beat; proof/illustration distinguished; opening and audio plan recorded |
| Obtain assets | [asset playbook](asset-playbook.md); [generation recipes](generation-recipes.md) only for a real gap | Capture actual moving sources first where useful; obtain music/SFX; author only missing explanations | Selected visual/audio files opened, checked, indexed and hashed; music present or explicit blocker |
| Assemble | [shot recipes](shot-recipes.md), `production/editor/README.md` | Build timeline, useful motion, short captions, audible music and stronger action accents; inspect and render | Playable MP4 has the intended musical bed and SFX, not only an audio stream |
| Judge/revise | [quality procedure](quality-procedure.md) | Inspect opening energy/diversity, useful motion, meaning, reading time and audible mix | Review names the exact render, music/SFX observations and motion checks; limits explicit |
| Deliver | `production/delivery/README.md`, Skool/ManyChat references | Package video, assets, editable files, giveaway and verified task/release links | User can open the video; publishing/delivery states are reported separately |

Do not read every source transcript or the entire repository into context. Load the selected take, current beat/asset list, relevant recipe, and current failing receipt. For a revision, read its changed beat plus the preceding/following beats.

## Calibrate before choosing visuals

For the supplied Council reference, read `production/reference/council-human/visual-profile.json` and inspect its representative frames. The reference's central property is a concrete visual action/metaphor matched to the spoken idea. It is not a sequence of titled explanation slides. Most of the measured human reel keeps the presenter visible; UI/document inserts occupy about 18% of that particular edit. These observations describe the reference, not quotas for a new script.

Save one comparison frame each for presenter, metaphor, UI/typing and source evidence when present. Record caption treatment, useful reading hold, framing and the action shown. Choose one short matching style sample before assembling the whole reel. An eight-second test with two mostly static information diagrams may improve semantic honesty but still fall short of this reference's motion and visual language.

For a new reference, create the same small profile from actual observed frames/playback and measured cut candidates; do not invent exact fonts or sound-effect identities. Keep observations separate from editorial interpretations. Reuse an existing profile only when it describes the supplied reference.

## Exact working commands

Run from the repository root. Replace example paths with existing files; use new output directories per run. These commands are helpers, not an unattended end-to-end agent.

```bash
# Optional: transcript/index for a NEW complete filming batch.
python3 production/intake/intake.py --source /absolute/master.mp4 \
  --drive-metadata production/intake-source.json \
  --out production/intake/runs/NEW-RUN --work-dir /absolute/work/NEW-RUN --threads 4

# Apply inspected source-relative trims and map the words.
python3 production/prepare_take.py --source /absolute/source.mp4 \
  --transcript /absolute/source-transcript.json --edit /absolute/edit-decisions.json \
  --output /absolute/work/NEW-RUN/aroll.mp4 --words-output /absolute/work/NEW-RUN/words.json

node production/capture_evidence.cjs --sources /absolute/sources.json --out /absolute/work/NEW-RUN/captures
python3 <plugin>/scripts/reel.py run build -- --spec /absolute/timeline.json --project /absolute/work/NEW-RUN/composition
production/editor/node_modules/.bin/hyperframes check /absolute/work/NEW-RUN/composition --at 1,5,10 --json
python3 production/editor/edit.py render --project /absolute/work/NEW-RUN/composition \
  --output /absolute/work/NEW-RUN/raw.mp4 --quality high --workers 2
python3 production/finalize_render.py --input /absolute/work/NEW-RUN/raw.mp4 \
  --output /absolute/outputs/NEW-RUN.mp4 --receipt /absolute/verification.json
python3 production/check_editorial.py --map /absolute/editorial-map.json
```

For Samin edits, set `audio_policy.music_required: true` and add the actual music entry using the editor README contract. The plugin build command rejects a missing policy or track unless `audio_policy.user_opt_out` records Samin's explicit exception. Copy `<plugin>/templates/creative-review.json` to the pilot directory and fill observed fields as the work proceeds.

The intake requires a cached Whisper model and the Python packages in `production/requirements.txt`; read its setup before running. The editor's Node packages come from `npm ci` in `production/editor`. `prepare_take.py` currently uses macOS `h264_videotoolbox`; on another OS change only that encoder to available `libx264` after checking FFmpeg, then verify the output. It overwrites its named outputs: give it new paths. Do not repeatedly transcribe an unchanged batch.

An EDL uses source seconds, e.g. `{"speed":1,"segments":[{"start":2.2,"end":7.6},{"start":8.1,"end":13.4}]}`. These numbers are a format example, not approved cuts. Cut between words, preserve breath/natural cadence and inspect at least the last spoken sentence after a proposed ending. If `prepare_take.py` already made continuous A-roll, the renderer's source segments should normally be `[0, edited_duration]`; do not apply the original cuts a second time.

**Tighten small intra-sentence pauses for Samin's fast-paced reels, not only failed takes.** Use the actual waveform and verified word boundaries to locate idle gaps. As a review starting point, inspect gaps longer than roughly 180 ms and shorten expendable silence toward 70–120 ms where the phrase still sounds natural. These numbers are candidates, not automatic deletion thresholds: quiet consonants, a deliberate emphasis, a necessary breath or a sentence boundary may need more space. Preserve every intended word, consonant, natural join and the full CTA; keep the original speaking speed unless Samin asks otherwise. An ASR timing gap alone is not proof of silence.

Apply approved micro-pause cuts through the frame-aligned keep EDL, retain their source ranges and reasons, then verify each audio join in context. Any speech trim changes the timebase: rebuild the word map and retime **every** caption, shot, label, music cue and SFX cue before rendering. Recheck late-reel sync and the final word; never keep old absolute placements after tightening the voice. Use the existing CFR workflow below and preserve a copy of the prior edit.

For an existing timeline, run `prepare_take.py` first to create the tightened A-roll and new word list. Then use the reusable retimer rather than shifting timeline timestamps by hand:

```bash
python3 <plugin>/scripts/reel.py --project /absolute/checkout run retime -- \
  --spec /absolute/old-timeline.json \
  --cuts /absolute/pause-removals.json \
  --source /absolute/new-aroll.mp4 \
  --words /absolute/new-words.json \
  --output /absolute/retimed-timeline.json
```

`pause-removals.json` has `{ "source_duration": OLD_OUTPUT_DURATION, "cuts": [{"start": REMOVED_START, "end": REMOVED_END}] }`, replacing the uppercase placeholders with measured seconds. Its cuts are ordered, disjoint removed intervals on the **old output clock**, not the original filming-master clock unless those clocks are identical. This removal list is separate from the keep EDL used to prepare the new A-roll. Its `source_duration` must match the old timeline's summed `source.segments` duration; the helper rejects a mismatch.

The retimer remaps shots, labels, zooms, flashes and SFX onset times; points `source` at the complete tightened clip; and uses the new words while retaining caption phrase word indices. Use it for pause removal with unchanged intended word order, and verify new video/word durations and phrase coverage before building. It rejects an already music-configured timeline: preserve that version, remove its old music configuration from a working copy, retime speech/visuals, then **replan a continuous bed and its beats on the final clock**. Do not chop music at each removed speech gap.

The helper does **not** retime actions baked into B-roll, source-video offsets, generated scene internals or the natural duration of an SFX file. Recheck typing, cursor clicks, results and effect tails against the new spoken anchors; manually trim/re-author affected visuals when needed. A fully removed shot/event requires an editorial decision rather than a silent deletion. The emitted `retime_review` is a work reminder, not proof of audiovisual sync.

For a verified constant-frame-rate proxy, add `"frame_rate":30` (or its actual rate) to the EDL and place every cut on that source frame grid **after checking speech handles**. The helper validates the declared rate and boundaries, trims exact frame indices and bypasses tempo processing at speed 1. It rejects off-grid cuts instead of moving them silently. Probe metadata alone cannot establish constant frame rate; use a known CFR proxy. Legacy EDLs still use timestamp trims, whose video-frame padding can make later audio/words drift from the ideal summed duration. Verify actual output duration and joins before accepting their retimed captions.

Treat implausibly long ASR token spans (review ordinary single words over roughly 1.2 seconds), repeated zero-duration tokens or missing restart text as an intake defect to investigate. Transcribe the suspicious source interval with short surrounding handles, inspect its waveform and compare the repetitions before choosing a cut. Mobbin's 3.3-second `library` span hid a repeated sentence; a stretched `600,000` hid two failed starts. Do not just delete an apparent gap inside that token. After cutting, compare a fresh transcript of the actual A-roll with the selected speech, retaining the complete CTA. ASR/waveform checks do not constitute human listening approval.

## Reuse versus discovery

Council v2 is the current concrete editing example: `production/pilots/council-v2/README.md`, `timeline.json`, `editorial-map.json`, `asset-index.json`, and the private release recorded in `release.json`. Use its visual grammar and data shapes. Its 35.9 seconds, 18 shots and 50 caption groups describe that performance; they are not quotas for future reels.

If a tool fails, read the error once, check its documented input, make a specific correction, then retry. After two materially different attempts fail, record that dependency as unavailable and take the recipe's fallback. Do not repeatedly guess selectors, generation flags, account IDs or download URLs. Continue independent work, and identify the exact missing dependency if it prevents delivery.

## Smaller-model handoff prompt

> Use the Samin Reel Engine plugin's `reel-director`, resolve the project with its runner, and read the operator runbook. Resume the existing reel at the stage in `operator-state.json`. Work only on this reel. Follow the current stage's linked recipe; prioritize relevant real moving B-roll, use full-screen footage when useful, and give static proof a readable directed camera move. Put the highest useful action and diversity in the first 3–5 seconds. Include audible instrumental music unless Samin explicitly opted out, map key reveals to beats, and make SFX clearly audible while preserving every spoken word. Calibrate against the supplied style reference when present; a matching finished example is not required. Save beat-to-visual decisions and `creative-review.json`, then run existing helpers. Deliver an actual video and its review receipt. Do not infer completed research, captured screens, generated media, human playback approval, publication or DM delivery. If blocked, name the exact failed input/tool and continue independent stages; never silently omit music.
