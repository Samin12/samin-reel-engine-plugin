# Shot recipes: decide what happens on each spoken beat

Lock the edited words first. Fill the editorial map before assembling: viewer question → visual job → asset → important word → reveal → stable hold → expected takeaway. Use `production/editorial-map.schema.json` and the completed Council map for the exact data shape. Every word must belong to a beat; one shot can cover multiple related beats.

## Place and size the shot

Find the important noun or verb in the final word list. Place the relevant visual change near that word; a short lead can orient the viewer, but write why it helps. Use the preceding beat to establish source identity when the proof crop needs all the next beat's time. Do not cut to an unrelated new image simply because two seconds elapsed.

As an initial estimate, reserve roughly 0.2 seconds for a reveal and 0.8–1.4 seconds of stillness for two to seven focal words. These are planning estimates, not automatic pass thresholds. If the reader needs more: show fewer required words, enlarge the crop, simplify the treatment or use more of the spoken beat. Do not count typing/scrolling time as a completed-text hold.

At 1080×1920, Council uses a 0.4648 top split, a large lower presenter, and captions near the boundary. Choose split when both face and visual remain useful. Use full-screen evidence when the required mechanism cannot be read in half a frame. Use the presenter for a short pivot instead of squeezing in another asset. Keep source attribution small but readable; the explanatory focal words must be much larger.

## Opening energy and moving B-roll

**Make the whole graphic hook understandable in one paused frame.** Subject, specific payoff, supporting detail and their relationship must be visible **simultaneously in the first encoded frame** at phone size, without sound or the brief. Animation may reinforce that meaning but must not be necessary to decode it or reveal an essential missing label later. Use one dominant subject and a large, contextualized count, result or contrast when the hook calls for one. A giant number without its unit, subject and context fails. Support concise hook copy with a real useful visual; do not turn the intro into a paragraph card.

**A clear paused frame is not permission to hold an unchanged intro image.** In the first 3–5 seconds, prefer no more than about **0.5 seconds** before a useful visible action/view change, with **1 second the maximum unchanged hold** unless Samin explicitly changes that direction. Text may stay legible while the supporting B-roll changes. Use an actual UI action, a meaningful new source view/detail, or a clear move into active full-screen footage. Hidden/subpixel animation, caption changes over the same inert image and a tiny slow zoom alone do not supply the required intro energy. This limits unchanged visual holds, not every shot's duration; a longer shot with useful continuous action can work.

A useful option is **Samin below + the complete clear graphic above for roughly the first 0.5 seconds**, then active full-screen B-roll that preserves the subject/payoff relationship. Choose it when the face establishes the hook; it is not mandatory for every reel. Keep the initial meaning complete and readable while the visual experience changes. If a dense proof crop needs a long still read, simplify the opening and move that reading task to the body instead of keeping the intro inert or making text unreadable.

Make motion reinforce the already visible relationship/result and settle long enough to recognize it. Eye-catching scale and contrast should direct attention to that one idea. For Mobbin, busy category menus may show activity but fail to communicate the hook. A clearer treatment is **“600,000+ real app screens for Claude Code”**, supported by actual app-screen examples, a clear library-to-Claude relationship and source attribution. This is a sourced editorial graphic, not a claim of an executed Claude result. Confirm the count/source for the current script. This example is not a mandatory layout for every reel.

Use clear editorial framing and source attribution for obvious stat cards, collages, arrows and montages; they do not need a technical “illustration” badge merely because they were authored. Add an explicit reconstruction/illustration label when the content could reasonably be mistaken for a live interface or a generated/executed result. Never fabricate execution proof. Keep labels useful to the viewer instead of explaining the production process unnecessarily.

See the packaged [Mobbin hook decision](https://github.com/Samin12/samin-reel-engine-plugin/blob/main/plugins/samin-reel-engine/examples/mobbin-hook.json) and [actual encoded phone-size frame](https://github.com/Samin12/samin-reel-engine-plugin/blob/main/plugins/samin-reel-engine/examples/mobbin-hook-frame.png) for a concrete hierarchy example. The still does not establish opening motion quality. Copy the hierarchy principle, not the claim, asset selection or unchanged hold length.

Before polishing, run the [muted cold-view test](quality-procedure.md#first-frame-and-two-second-cold-view-test). If the viewer cannot identify subject, payoff and focal detail, simplify/reframe the hook before adding cuts or effects. More action alone does not repair unclear meaning, and no visual test guarantees retention or virality.

Samin's default is a music-backed, visually active reel. Put the strongest relevant action and greatest useful visual variety in the **first 3–5 seconds**. Plan the opening separately before distributing assets across the rest of the reel. Start with the complete readable hook; use motion, detail/reframes, music and accents to emphasize its already visible meaning. Keep essential subject/payoff/context visible through the opening. Ordered reveals must not delay those essentials. This is not a demand for three unrelated clips or a transition on every word.

Prefer actual motion inside the B-roll: typing, scrolling to a relevant section, a cursor selecting an option, a changing app state, a demo result, or a physical action. Use moving B-roll full-screen freely when it reads better or creates a stronger moment; the presenter does not have to remain visible. Vary the visual experience through different relevant sources, source regions, shot scales and layouts. A close detail, wider context and actual action can create useful diversity within one source. Repeated zooms on the same unchanged screenshot do not provide the same diversity as a new useful view/action.

In the body, when a static proof image is the strongest source, normally add a **slow, directed zoom or reframe** instead of leaving it inert. Start around 1.00→1.03–1.08 scale over its 2–4-second shot, or move from source identity toward the relevant detail. These are starting ranges, not fixed requirements and do not override the opening's faster action rule. Keep required text, identity and qualifications inside the crop at both ends; inspect both encoded endpoints at phone size. Let a reveal settle before the important reading hold. For dense text, reduce or stop movement during reading rather than sacrificing legibility. Record an intentional still hold when motion would weaken the proof.

Mark each shot's visual action and each opening focal change in the edit's `creative-review.json` (fields in [quality procedure](quality-procedure.md)). Maximize relevant visible action, not random movement. Never fabricate product behavior, fake scrolling/typing proof, flash unrelated assets, or speed up a measured demonstration without making the time compression clear.

## Pick a recipe

| Recipe | Sequence and timing | Sound/motion | Reject when |
|---|---|---|---|
| Repo/README proof | Establish original repo/owner → tighter relevant heading or command → hold | One small sweep for the crop change; gentle 1.00→1.03 image scale if useful | README is irrelevant, text is microscopic, or stars substitute for capability proof |
| Tweet/announcement | Show author/date/source identity → focus exact clause → hold through spoken claim | Brief pop on reveal; static text during reading | Quote/context is missing, source is fabricated, or a statement is presented as a measured result |
| Real input/action/result | Orient in app → enter concise input → execute → hold actual result | Audible light typing clicks only while typing; one distinct click at the action | Only typing was captured but narration implies a successful result |
| Before/after | Same relevant area and example → change state → hold difference | Hard cut or restrained transition; one accent at the change | Inputs differ or the comparison implies an unsupported performance claim |
| Roles/counts | Show exactly the narrated entities → emphasize the active one on its name | One small emphasis per role, stable design across related shots | Count changes, roles drift, or animation creates a fifth “extra” entity |
| Diagram/mechanism | Reveal input → active step → output while those steps are spoken | Directional highlight/crop follows the relationship | Arrows/labels become an unreadable whole-page diagram |
| AI/stock metaphor | One recognizable object/action for the concept, then return to evidence or presenter | Short visual action; avoid a competing narrative | It impersonates a real product result or needs explanation itself |
| Giveaway/CTA | Actual resource title/contents → useful exact excerpt → presenter/keyword | Paper flick or soft accent; concise caption keyword | Preview is unrelated, filename is invented, or a local file implies successful delivery |

Council examples: GitHub at 4.37s, evaluator diagram at 21.43s, session heading at 27.73s, actual follow-up prompt at 30.17s. Their job is evidence about documented mechanisms/resource contents, not proof of an executed four-agent product. The pixel characters are reference illustrations. Do not reuse these source claims in a different script without checking relevance.

## Use the existing timeline renderer

Paths resolve from the timeline JSON. Supported layouts are `presenter`, `split`, `full_broll`. Video media uses `source_start` in seconds; images use nondestructive `media_crop: [x,y,width,height]` in source pixels. `media_zoom` is a subtle wrapper scale, not a source-content change. A source label goes in the top-level `labels` list. Use the actual asset index to supply IDs/provenance; timeline media paths alone do not document evidence.

```json
{
  "id":"shot-04", "start":4.4, "end":6.8, "layout":"split",
  "caption_y":44.7, "media":"broll/actual-readme.png",
  "media_crop":[660,705,2100,570], "background":"#f6f8fa", "media_zoom":1.03
}
```

This crop is an example for the saved Council image; remeasure source pixels for every other image. Out-of-bounds crops fail the build. Do not paste this rectangle onto a different resolution. For a video shot, use `"media":"broll/recording.mp4", "source_start":2.1, "fit":"contain"` and verify that the remaining clip covers the shot. `contain` preserves required edges; `cover` can remove them.

For the actual giveaway, `scene.kind: "artifact_preview"` displays filenames and exact excerpts. See `production/editor/editorial_scenes.py` and the Council timeline. Read the real files before filling `files`, `active`, `excerpt` and `reveals`. This is an authored resource preview, not a captured app. Show a short excerpt; do not paste an entire prompt into the frame.

## Captions in this reference style

Start from Council v2's caption settings: Arial Black, white text, lilac `#D4A1F7` on a few important words, subtle dark stroke, about 78px at 1080 width. Its small connector phrases use regular mixed-case text; important phrases use heavier uppercase. Scale these values with output size and check the actual face/background. Exact original font identity is not established.

Use this explicit starting preset at **720×1280** (52px is the scaled equivalent of 78px at 1080). Copy the same values from `<plugin>/templates/council-caption-preset.json`; this is a partial timeline, not a complete edit:

```json
{
  "output": {"width":720,"height":1280,"fps":30,"split_fraction":0.4648},
  "captions": {
    "font_size":52,"font_family":"Arial Black","accent":"#D4A1F7",
    "uppercase":true,"hold":0.06,"max_words":3,"max_chars":24,
    "omit_terminal_punctuation":true,"background":"rgba(0,0,0,0)",
    "emphasis":[]
  }
}
```

Fill `emphasis` with a few actual meaningful words from the current script. Setting `accent` without selecting words produces no lilac emphasis. Keep the caption background transparent; opaque black panels were a visible mismatch in the first smaller-model trial. A justified difficult background may need a local treatment, but do not impose a black plate across the whole reel. Start `caption_y` at 44.7 for split shots and 62 for presenter shots; inspect full-screen placement against that asset's focal detail.

Group by spoken meaning, generally two to four words. Avoid splitting “AI agents,” a product name, a negation and its verb, or the CTA keyword. Keep at most two useful lines. `captions.phrases[].word_range` uses zero-based start-inclusive/end-exclusive indices. The complete list must cover each actual word exactly once. `line_breaks` are positions within that phrase; `lead_in:true` softens its first line. Retiming speech requires rebuilding these groups from the updated word map.

**Explicit `phrases` bypass `max_words` and `max_chars`.** Count words in every manual range. Two six-word ranges do not become three-word captions when you change `max_words`. `lead_in:true` applies to the entire first line: use it on a real connector, not a whole emphasized sentence. A longer inseparable name may justify an exception; record and inspect it.

Do not manually add an unspoken word to fix a weak sentence. Correct an ASR spelling only after checking the audio. Do not let a caption sit over an essential UI label. Move the caption or change layout for that shot rather than shrinking everything.

## Music, beats, SFX and VFX

**Instrumental background music is required by default for Samin's reels unless he explicitly opts out for that reel.** Do not silently omit it because no candidate is preloaded, an audio helper describes music as optional, or a provider fails. Select a rights-cleared track or create an original instrumental using an available authorized tool. Prefer a clear rhythmic pulse, useful accents and no competing vocals. Follow the sourcing/fallback procedure in [asset playbook](asset-playbook.md); an unresolved music dependency means the edit is an incomplete review candidate, not a completed music-backed reel.

Map music to the locked voice before the final render: choose the musical in-point, mark audible beats/accents, place the strongest useful energy in the first 3–5 seconds, and identify section changes and the ending. Put selected reveals, crop changes, clicks and payoffs near meaningful musical accents while keeping their spoken anchors intact. Do not stretch or chop Samin's words to force every cut onto a beat. Maintain the bed through the body and CTA, allow deliberate brief dips for emphasis, and end on a clean musical tail/fade after the final word. A track present in the timeline but inaudible in the export has not met this requirement.

For a fresh reel, mix Samin's current voice with separately identified music and effects. Never put an old narration under a different script. If a same-script full reference soundtrack already supplies the intended voice/music/effects, verify those layers in playback and avoid adding duplicate music or SFX.

**Make SFX clearly audible and more assertive than the first Mobbin pilot.** Give the intro its strongest purposeful accents, then accent real clicks, reveals, crop changes and major payoffs throughout. As mix starting points, place the music bed roughly 14–20 dB below the active voice's average level, and selected transient effect peaks roughly 4–8 dB below nearby voice peaks; compare like measurements over the same speech region. These ranges are calibration aids, not pass thresholds or universal file gains. Raise a weak effect until it reads at normal phone volume, then move, shorten, EQ or reduce it if it masks a word. Duck the bed temporarily beneath dense speech or an important phrase and let its energy recover. Do not achieve a louder mix by clipping or burying consonants.

The original synthesized starting set is in `production/pilots/council/sfx/index.json`:

- `small-tick.wav`: typing/click detail; legacy starting gain 0.22, raise if it fails the audibility check.
- `soft-sweep.wav`: crop/screen transition; start gain 0.30, lead its envelope into the cut.
- `paper-flick.wav`: resource/document appearance; start gain 0.30.
- `rounded-impact.wav`: one meaningful verdict/reveal; start gain 0.16.

Those legacy gains are asset-specific starting points, not final targets, universal loudness values or the exact human-reference effects. Do not copy them unchanged if the result is too quiet. Use top-level `sfx` entries such as `{"path":"sfx/paper-flick.wav","at":5.1,"gain":0.30}` and calibrate against the current voice/music. Copy the correct files and provenance into the reel's asset index. One repeated whoosh on every cut flattens the accents; choose clicks, swishes, impacts or ticks that match what moves. Listen to the complete mix at normal phone volume, check music and effects are perceptible, and preserve speech clarity and a clean ending.

Use hard cuts, small punch-ins, directed crop moves and restrained caption pops to support the words. No mandatory transition quota, flashes or random zooms. In the renderer, crop backgrounds must be timed clips; an opaque untimed layer once hid earlier B-roll despite passing browser checks. Verify encoded frames after any layering change.
