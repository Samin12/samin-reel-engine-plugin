# Quality procedure: separate a playable export from a good edit

Read `production/editorial-judgment.md` for the five scored dimensions and hard failures. This procedure tells a smaller model what to inspect, what evidence to save, and what to do with a failure. A missing observation stays missing; do not fill review fields with assumed success.

## Before the expensive render

1. Check every planned beat against the actual words. Its asset must answer the viewer question; a relevant URL alone is not enough. Check every selected file exists, was inspected, and matches its indexed hash.
2. Check static source claims against the original source. Read the exact crop, not just its heading. Count figures/roles manually where a number matters. Read app/model names and compare input/output examples. Remove wrong or irrelevant evidence.
3. Check a frame near each shot's first useful moment and reading hold. Empty/black/covered B-roll, clipped faces, hidden captions and tiny required text are failures. If source text is dense, crop to the specific clause rather than shrinking a whole page.
4. Run HyperFrames check on the built project. Inspect its actual errors/warnings; do not call disabled motion assertions passed. The editorial checker checks structure and joins, not truth or readability.
5. Confirm the actual instrumental music file, selected in-point and beat/energy map exist, unless Samin explicitly opted out. Verify opening action/diversity, moving B-roll source bounds and both endpoints of each static-proof zoom. Missing music is a completion failure even if the MP4 has a valid voice/SFX stream.
6. Review intra-sentence idle gaps as well as false starts. For gaps above roughly 180 ms, inspect waveform and real word boundaries; shorten expendable silence toward 70–120 ms only where the phrase remains natural. Check the frame-aligned keep EDL preserves consonants, breaths that carry delivery, every intended word and the complete CTA. After any cut, confirm words, captions, shots, labels, music and SFX all use the new timebase. ASR gaps and silence-detector output propose cuts; they do not approve them.

Before approving a sourced shot, finish: **“At [time], I can read/recognize [exact focal detail]; it explains [specific spoken action/relationship].”** If the answer is only “the page is there” or “it says the same noun,” selection failed. Save the proposed crop and the rejected alternative. Compare reference/candidate caption frames at equal display size before rendering the full cut; matching resolution alone does not match typography or treatment.

Observed lower-tier regression: an eight-second test passed all render checks but showed a tiny full Wikipedia Judge page, an INVESTOR question card and opaque black caption panels. Those are a semantic fit/readability/style failure, not a successful proof-visual workflow. Replacing the screenshot with another whole page or making the captions larger does not repair the underlying issue.

## Review the actual encoded MP4

1. Run `production/finalize_render.py` on a new output path. It performs a complete decode, normalization and hash receipt. Council's working target was about -14.2 LUFS and -1 dBTP; it is a reference calibration, not a guarantee of identical perceived loudness. Check both stream durations and that the final spoken word remains intact.
2. Extract encoded frames at opening, each meaningful reveal, and the final CTA. Inspect the encoded output, not only HTML snapshots. A previous untimed opaque layer hid B-roll in the render even though browser checks were clean.
3. Watch the whole candidate at normal speed with sound. Check lip sync, first/last word, clause continuity, reading time, accents, abrupt audio ends and whether each reveal meets its spoken anchor. Then replay risky spans with the preceding/following sentence.
4. Check at phone size. Can the required source detail be read once without pausing? Does typing reach a useful state and hold? Do source overlays compete with captions? Does a platform control area cover something essential? Use the actual destination layout, not one universal safe-area number.
5. Record visible/audible observations with timecodes, dimensions scored 0–4, and specific repairs. Default editorial passage requires at least 16/20, every dimension at least 3, no hard failure, complete beat coverage and the actual render watched. If the model cannot perceive full playback/audio, deliver a candidate with those gates pending and request the missing review; it cannot certify itself from images or predicted scores.

## First-frame and two-second cold-view test

Before finalizing the intro, show a fresh reviewer **only the actual first encoded frame, paused at phone size**, withholding sound, script, brief, source manifest and intended interpretation. Ask: **“What is this about, what is the payoff, and which visible detail/relationship made that clear?”** Save those answers before playing anything. Then show the first two seconds muted at normal speed and check that motion preserves the already complete meaning.

Pass requires subject, specific payoff, supporting focal detail and their relationship to be **visible simultaneously and understood from the single first frame**. A giant count without unit/subject/context fails; so does a hook whose necessary labels appear only after animation. Keep essential meaning visible through the opening while motion reinforces it. If the response is only “some app menus” or requires narration, repair the hierarchy, crop or concise promise. An operator already briefed on the script may perform an informed self-check, but must not record that as an unbriefed test; keep that observation pending until an appropriate reviewer is available. This checks comprehension, not guaranteed attention or virality.

Record `opening.cold_view` with `status`, `first_frame_path`, `first_two_seconds_path`, `display_width_px`, `muted`, `brief_hidden`, `reviewer`, `subject_response`, `payoff_response`, `focal_detail_response`, `first_frame_subject_visible`, and `limitations`. The three responses must come from the paused first frame, before animation; name the visible relationship in `focal_detail_response`. Use `passed`, `failed` or `pending`; keep missing responses null. The evidence belongs to the current `render_sha256`. Do not prefill intended answers as observations.

### Opening motion at scrolling speed

The still-frame test and motion test must both pass. Play the first 3–5 seconds at **1× and phone size**, then identify the first useful visible action and every unchanged B-roll/graphic hold. Aim for no more than about **0.5 seconds unchanged**; a hold **over 1 second fails** Samin's current intro direction unless he explicitly opts out. These are limits on unchanged images, not a random cut quota or a one-second cap on continuously useful moving shots. Tiny slow zooms, hidden/subpixel movement, changing captions, or the presenter's mouth moving below an inert graphic do not by themselves repair the B-roll's inactivity. Motion must visibly change a useful action, source view or focal detail while text/evidence stays legible.

Record `opening.motion_cadence` from the actual export: `first_visible_action_seconds`, `first_visible_action`, `shot_spans`, `unchanged_visual_spans`, `max_observed_unchanged_seconds`, `split_intro`, `normal_speed_checks` and `status`. Each span contains `{start,end,duration,observed}` in reel seconds; distinguish shot duration from unchanged duration. `split_intro` records `{used,duration_seconds,reason}` including the decision about an approximately 0.5-second presenter-bottom/graphic-top opening followed by active full-screen footage. Each normal-speed check records `{start,end,display_width_px,observed,evidence_path,reviewer}`. Template limits are 0.5 seconds preferred and 1 second maximum; leave observations null/pending until reviewed. Numeric timing alone does not prove that motion is useful, readable or likely to retain viewers.

## Check music, opening energy and motion explicitly

Samin's feedback on the first Mobbin edit makes these checks mandatory. Complete them against the **encoded final render**, not the intended timeline:

| Check | What to inspect and record | Repair when weak |
|---|---|---|
| Background music | At normal phone volume, listen to the opening, a speech-dense body span and CTA. Name the audible rhythmic bed and musical ending; record timecodes. A file or waveform alone cannot prove audibility. | Add the missing instrumental or raise/rebalance the bed; never silently deliver voice/SFX only without Samin's opt-out. |
| Beat/energy design | Mark observed accents and at least the opening, one body payoff and ending decisions. State whether reveals follow their spoken anchors and musical accents without awkwardly cutting speech. | Change musical in-point, accent placement or clip timing; preserve the spoken meaning. |
| Stronger SFX | Listen to the intro's strongest accent and representative body clicks/reveals. Identify sounds that are actually heard at normal volume, and check every nearby word is intelligible. | Raise an inaudible effect, or shorten/move/EQ it if it masks a consonant; do not simply maximize all gains. |
| First frame / opening | Run the cold-view test and 1× motion test. Log first action, shot and unchanged-image durations, split choice and useful changes across 3–5 seconds. Prefer ≤0.5 seconds unchanged; reject >1 second. | Keep the complete hook readable while a real action/view changes; try a brief presenter-bottom/graphic-top start followed by active full-screen footage. |
| Motion and diversity | Count seconds of actual recorded motion, authored motion, camera movement on stills and intentional still holds separately. Note distinct source types/views, split/full-screen changes and any repetitive run. | Replace weak static/repeated views with relevant moving footage; use full-screen motion or a new useful source region where it helps. More motion is preferred when it preserves comprehension. |
| Static-proof camera move | Inspect the start and end crop at phone size and a frame during its reading hold. Name the exact detail and qualification still visible. | Slow, reduce or redirect the zoom; use a justified stable hold rather than clipping evidence. |

Copy `<plugin>/templates/creative-review.json` beside the timeline as `creative-review.json`; it supplements existing schemas and is **not** a new renderer input. Populate observations after inspection. Do not convert planned numbers into observed results:

```json
{
  "render_sha256": "<actual reviewed render hash>",
  "music": {
    "status": "pending",
    "asset_id": null,
    "user_opt_out": null,
    "source_in": null,
    "beat_markers_seconds": [],
    "cue_checks": [],
    "energy_plan": [],
    "audibility_checks": [],
    "ending_check": "pending"
  },
  "speech": {
    "edl_path": null,
    "aroll_sha256": null,
    "words_path": null,
    "playback_speed": 1,
    "pause_cut_checks": [],
    "retimed_artifacts": [],
    "complete_speech_check": "pending",
    "first_word_check": "pending",
    "cta_and_last_word_check": "pending"
  },
  "sfx": {"accent_checks": [], "speech_masking_check": "pending"},
  "opening": {"window_seconds": 5, "observed_actions": [], "body_comparison": "pending"},
  "motion": {
    "recorded_motion_seconds": null,
    "authored_motion_seconds": null,
    "camera_move_on_still_seconds": null,
    "intentional_still_seconds": null,
    "distinct_source_types_or_views": [],
    "full_screen_motion_spans": [],
    "static_endpoint_checks": [],
    "repetition_findings": []
  },
  "playback_review": {"full_with_sound": false, "phone_size": false, "reviewer": null, "method": null, "limitations": []},
  "gate_results": []
}
```

Use music status `present`, `opted_out`, `blocked` or `pending`; `opted_out` requires Samin's actual instruction in `user_opt_out`. Audibility/accent checks should contain `{time, observed, repair_needed}`; opening actions should contain `{time, action, new_detail}`. Record music `energy_plan` as `{start, end, intent}` and timed spans as `{start, end}`. Treat motion categories as non-overlapping dominant treatments per span so their seconds are comparable; this is an editorial description, not an automatic quality score or minimum motion percentage. Record a deliberate still or unusual opening choice with its proof/readability reason. Keep unobserved listening or motion fields pending.

Make timing/evidence fields useful to the next operator:

- `music.beat_markers_seconds` uses **final reel seconds**, derived from the actual selected musical in-point. Each `cue_checks` entry names `{shot_id, spoken_anchor, beat_reel_time, visual_reel_time, observed, evidence_path}`. A planned beat grid and a detected BPM do not prove the revealed action feels aligned; note any deliberate lead/lag.
- Each SFX `accent_checks` entry also names `{asset_id, action_reel_time, audible_onset_reel_time, voice_words_at_cue, observed, evidence_path}`. Locate the sound's audible onset inside the file; placing a file with leading silence on the cut is insufficient. A sweep may intentionally lead a transition; document that choice instead of forcing identical timestamps.
- Each speech `pause_cut_checks` entry names `{source_path, source_clock, source_range, source_cut_frames, source_fps, final_join_time, gap_before_ms, gap_after_ms, adjacent_words, reason, join_observation, evidence_path}`. `source_range` is `[start,end]` in seconds of the named EDL input (master, proxy or prior edited A-roll); identify that clock explicitly. `source_cut_frames` is `[first,last_exclusive]` of the removed interval in that same input. Use actual measured values and the verified CFR source rate. `retimed_artifacts` lists the new word, caption, shot, label, music and SFX records. Set complete-speech checks only after normal-speed playback establishes that all intended words, consonants and the CTA survive. A matching ASR transcript is supporting evidence, not a listening substitute.
- Each `gate_results` entry names `{gate, status, observed, evidence_path, repair, recheck}` with status `passed`, `failed` or `pending`. Evidence may be a saved frame, short encoded review clip, listening note tied to the current hash, or a technical receipt appropriate to the claim. Record who or what actually perceived it and any limitations. Paths must point to existing artifacts; do not invent a completed review clip.

## Concrete pass/fail examples

These are **illustrative decisions**, not claims that a particular render already passed. Apply them to the current reel's actual times and files.

| Gate | A pass establishes | Fail or pending example |
|---|---|---|
| Music | The reviewer hears the rhythmic bed beneath intelligible speech in 0–5 seconds, a dense body span and the final CTA; the ending resolves/fades cleanly. The note identifies the current render and those spans. | `music.mp3` exists and LUFS passes, but no one checked the mix: **pending**. The bed is absent or cannot be heard at normal playback volume, with no opt-out: **failed**. |
| Beats and stronger SFX | The reviewer hears a distinct intro accent at the important visual reveal, plus clear body action accents, and can understand the nearby words. Cue records identify actual musical/visual/audible-onset times. | SFX file starts at 1.40 s but its silence delays the click until 1.85 s after the visible action; move its useful onset. A louder whoosh hides a word: **failed** until repaired. |
| Opening hierarchy | An unbriefed viewer understands the subject/payoff/detail/relationship simultaneously in one paused first frame. For Mobbin, actual app-screen examples with count, unit and Claude Code context make a clearly sourced editorial collage; no execution is implied. | Busy menus prompt only “some app website,” a giant number lacks a unit/context, or the Claude label arrives later: **failed** even if the full animation explains it. Informed self-check only: unbriefed test **pending**. |
| Opening motion | The clear split graphic lasts about 0.5 seconds, then a relevant full-screen action/view moves visibly at 1× while meaning remains legible. Or a different equally clear treatment supplies useful immediate motion. Actual spans and first action are recorded. | A clear graphic stays substantially unchanged for 4 seconds with only a 1% zoom: **failed**, even if every encoded frame technically differs. Unchanged holds over 1 second fail; a source file called “video” is no substitute for observed action. |
| Moving proof and diversity | A real recording shows the relevant settings action and resulting state, with enough time to recognize it. Another beat uses a different useful view/detail; full-screen motion is used when it improves the result. | An `.mp4` contains a frozen screenshot, or the same tiny crop repeats under several claims: motion/diversity is not established. An unrelated impressive demo does not become proof because it moves. |
| Static-proof zoom | Start, moving and end frames retain the product/source context and exact supporting clause at phone size. A gentle move leads attention and settles for reading. | The count/qualification is cropped out at the end, or constant panning prevents one reading: **failed**. Stop or redirect the move; an intentional readable hold can pass. |
| Pause cuts and 1× speech | A verified 300 ms quiet gap is shortened to roughly 100 ms using valid frame boundaries, the adjacent words sound complete at 1×, and every later cue uses the rebuilt time map. A deliberate pause can remain with a reason. | A silence detector removes the start of a soft consonant, a 1.1× speed-up is substituted without instruction, the CTA loses its last syllable, or captions retain old times: **failed**. No actual listening: **pending**. |

Run the final gates in this order: **complete speech and timing → source honesty/readability → opening and motion → music/SFX mix → whole-reel normal-speed review**. Repair in that order when defects interact: changing speech after a sound pass invalidates its cue timing, and changing the mix invalidates prior listening approval. A missing observation stays `pending`; a known violation is `failed`. Both prevent a claim of final editorial passage. Continue useful repairs, and show a candidate with its exact remaining review need when perceptual access is unavailable.

Judge representation from the actual graphic. An obvious sourced montage/stat card does not fail for lacking an “illustration” badge. Require explicit reconstruction/illustration labelling only when a viewer could mistake authored content for a live UI or generated/executed result; preserve clear attribution and reject any false execution claim.

## Synchronized comparison tool

For two aligned versions of the same performance:

```bash
python3 production/build_review.py --reference /absolute/reference.mp4 \
  --candidate /absolute/candidate.mp4 --out /absolute/outputs/REEL-comparison \
  --title 'Reel comparison' --moments /absolute/review-moments.json
```

`review-moments.json` is a list such as `[{"time":4.4,"label":"README reveal"}]`. Open the output `index.html` in a browser. Play both together, choose one soundtrack, seek to a relevant beat, or select Candidate only for a larger phone-like view. The package contains original MP4 copies and their hashes. Equal duration does not prove alignment; establish that separately. Compare an unrelated style reference independently instead.

The player, successful playback automation, a contact sheet, ASR, loudness analysis and provider scene descriptions do not automatically set editorial approval. The review record must state what the reviewer actually observed.

## Optional automated second opinion

Higgsfield's scene analysis can supply a whole-clip scene/audio summary. Its timestamps are coarse and its visual interpretation can be wrong. On Council v2 it reported five characters in a four-character illustration; direct frames at 6.98, 7.50, 8.20 and 8.90 seconds showed four. Preserve that discrepancy as a rejected machine finding. Do not edit a correct shot solely to satisfy a model's mistaken description.

An available hook/attention predictor can inform creative experiments, but its score is not evidence of actual retention, virality or editorial correctness. Record its provider, exact input hash, status, findings and limitations separately from the editorial rubric. Compare suggestions to actual frames, narration and sources before changing the edit.

Use this prompt for an independent reviewer with the actual video and source manifest:

> Inspect the provided final reel and any supplied style reference. For every spoken beat, describe what is actually visible and the viewer question it answers. Check audible instrumental music, beat-supported reveals, stronger purposeful SFX, the first 3–5 seconds' action/variety, moving and full-screen B-roll, and safe slow zooms on static proof. Identify unsupported proof, wrong entities/counts, illegible focal details, repetitive or inert shots, mistimed reveals, distracting captions and sound that masks speech. Report exact timecodes and one actionable repair per defect. Distinguish observations from uncertainty. Do not infer live product execution from a reconstructed interface. Do not assume the source manifest proves the rendered pixels match it. State whether you watched the full video with sound, what phone-size checks you performed, and any tool limits. Score only dimensions you can actually assess.

## Repair table

| Failure | First repair | If still weak |
|---|---|---|
| Real source is irrelevant or misleading | Replace it with evidence for the actual claim; narrow claim if needed | Presenter or identified explanation; keep evidence gap explicit |
| Required source words are tiny | Crop tightly while retaining needed identity/qualification | Full-screen insert, fewer required words or longer hold |
| Typing/scrolling finishes too late | Cut dead setup/waiting and hold the completed useful state | Before/after stills with honest presentation, or a different shot |
| Too much text | Keep one focal phrase; use short captions; remove redundant graphic copy | Show a concrete action/object instead |
| Weak proof timing | Move reveal/crop to the important noun or action | Split the beat into setup and payoff |
| Generated count/identity changes | Revise with an approved still and explicit count/action | Deterministic illustration or relevant real asset |
| Missing or inaudible music without Samin's opt-out | Obtain a playable instrumental and mix it audibly beneath the voice | Follow provider fallback; label the preview incomplete with the music blocker |
| Intro is static or visually weaker than the body | Lead with the strongest relevant motion/result and a useful detail/payoff | Reframe static proof deliberately; preserve reading time and source context |
| Repetitive B-roll or gratuitous motion | Change the relevant action, source region, scale or full-screen/split treatment | Replace weak footage; keep an intentional still when it gives stronger proof |
| SFX too quiet to register | Raise the selected accent while listening with voice and music | Choose a clearer/shorter effect or move it into a gap |
| SFX masks a word | Lower or move that effect; listen in context | Remove it; voice clarity takes precedence |
| Intra-sentence pauses make the delivery drag | Verify the actual quiet gap and shorten it with a frame-aligned keep EDL | Preserve a natural join; retain the pause if it carries meaning or protects speech |
| Tightening clips a consonant or causes later cues to drift | Restore speech handles and rebuild the complete time map/cues | Recheck every changed join, late sync and the final CTA at normal speed |
| Blank or frozen visual | Inspect timed layers, media duration/source offset and renderer output | Replace/fix the asset; do not silently loop broken footage |
| Last syllable missing/audio tail wrong | Check sample/timestamp continuity and actual decoded tail | Correct finalizer/input timing, then re-export and verify |
| Goal requires playback the model cannot assess | Keep review pending and provide an easy comparison artifact | Obtain the missing perceptual review; never fabricate a pass |

After a repair, inspect the changed span and its neighboring beats, then re-render. A changed output hash invalidates prior full-render approval. Unchanged encoded video packets can preserve frame observations through an audio-only remux, but audio observations need refreshing. Run `production/check_editorial.py --map /absolute/editorial-map.json` after updating the real map; its output must still say semantic review is required.

## Finish the handoff

### Lessons from the Mobbin blind edit

The Mobbin pilot used another raw take without a matching finished reel. Its first-frame review caught three practical errors before delivery: a welcome screen used for the word “profiles,” a desktop typing strip too small to read, and a count buried under a larger generic headline. Replace an adjacent category with the exact visible noun (avatar/name/Profile controls), punch into the active instruction, and crop the original count clause at the count's spoken moment. A source being authentic does not make its placement useful.

For full-screen phone clips, inspect both outer edges in the actual render. `object-fit: contain` on a video can leave the presenter visible at the sides in the native compositor even when the video element has a CSS background. The editor now places a separately timed full-panel background behind every media insert. Verify that it disappears when the presenter returns. Keep the source recording's audio muted and align deliberate SFX to the recorded or illustrated action.

The editable example and its proof inventory live at `<project>/production/pilots/mobbin-v1/`. Its original redesign illustration is explicitly labelled; official product demos are attributed and never described as an authenticated run performed by this pipeline. The real MAP giveaway contains setup guidance and original prompts, not a copy of the third-party screenshot library. Frame inspection and mechanical checks remain separate from Samin's playback approval.

Samin's playback feedback on that pilot identified a missing music bed and requested stronger SFX, more opening action, slow zooms on static evidence, more diverse views and more moving/full-screen B-roll. A technical/audio-stream pass did not catch the missing creative layer. Carry these requirements forward through asset sourcing, assembly and the explicit checks above; a later revision must be judged from its own actual render.

Deliver the final/candidate MP4, optional comparison package, editable timeline, source/asset index, real giveaway and review receipt. Push the skill/code/metadata to the existing local project repository; use release assets for large review exports. Verify uploaded sizes/hashes. Update existing Multica records with the exact version and observed status. Keep credentials out of Git. A private release is not an Instagram post, Skool post or ManyChat delivery. Use the existing delivery workflow when publication is actually requested.

The system's smaller-model usability should be tested with a fresh model and a bounded new reel/shot assignment. Keep its output and errors, then refine the instructions. Until such a test succeeds, describe this as a detailed, checked playbook—not a proven guarantee that every weaker model produces the same quality.
