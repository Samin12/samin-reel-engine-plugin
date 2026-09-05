# Asset playbook: where to look and what to keep

Use this during research and again after word timing is locked. Read [visual evidence](visual-evidence.md) for provenance rules. An asset is useful only if it helps the viewer understand this particular spoken point.

## Choose the visual job first

For each beat, fill this sentence before searching: **“When Samin says ___, the viewer needs to see ___ because ___.”** Assign proof, explanation, metaphor or presenter. Then follow the first applicable row:

| Spoken point | Search/capture target | What must be visible | What it establishes |
|---|---|---|---|
| A launch or announced feature | Original maker post, official changelog/release | Author/product, date/version, exact feature clause | The source announced/documented it |
| A GitHub tool or open source workflow | Official repository, README section, release, license | Owner/name then the relevant heading/command; required qualifications | Repository contents/terms, not an executed result |
| A specific result or speed/quality comparison | Original test, input/output pair, benchmark methodology | Same input, reported metric and relevant conditions | Only the shown observation; do not imply broader guarantees |
| “Type/connect/click/upload” | Real app recording of that exact action | Recognizable app, actual input, visible action and resulting state | The recorded action; typing alone is not success |
| Someone's statement or testimonial | Original tweet/post/interview | Exact quote, identity/date and context | That person said it, not that the claim is universally true |
| A saved resource or giveaway | Samin's actual file/page/repository | Title, useful excerpt, real contents | The resource exists and contains the excerpt |
| An abstract relationship | First inspect a relevant real source diagram; otherwise author/generate a simple illustration | Correct entities/counts and one relationship | Explanation, not empirical proof |
| A transition, opinion, warning or CTA | Presenter, perhaps a single keyword | Face/gesture and concise caption | Samin's delivery; B-roll is optional |

## Search in this order

1. **Eden:** search the subject/product plus synonyms. Open the saved item, then its original link. Use `saved-resources.md`; retain the saved-item ID. Bookmarks are also giveaway candidates. Do not mistake the save date for the event date.
2. **User assets:** inspect the supplied Drive folder, previous reel's asset index and this reel's own resource files. Reuse only assets relevant to the new claim. A prior Council illustration does not prove a new tool works.
3. **Primary web:** use exact queries such as `PRODUCT official release FEATURE`, `site:github.com/OWNER/REPO FEATURE`, `site:docs.PRODUCT.com FEATURE`, or the original author's post plus distinctive phrase. Use installed web/Firecrawl tools. Open results rather than using search snippets as evidence.
4. **Visual search:** search the named physical thing/action for original images, screenshots, clips or an appropriate meme. Follow the result to its source and inspect reuse terms. Stock footage illustrates a concept; it cannot validate product behavior. A meme should reinforce the line without creating another reading task.
5. **Generate/author:** only after identifying the actual missing visual job. Read `generation-recipes.md`. Do not generate fake tweets, repos, benchmark tables, app output or testimonials to fill an evidence gap.

Timebox an ordinary beat to three distinct searches and inspection of the most promising results. If nothing useful appears, change the treatment: show an actual resource excerpt, use the presenter, or make a narrow illustration. Do not turn a weak source into proof because the search took time. Save rejected leads with a short reason so the next agent does not repeat the search.

## Prefer motion when selecting B-roll

For equally relevant, readable candidates, prefer an actual moving clip over a static screenshot. Search explicitly for the action: an official demo, input/result recording, UI flow, product walkthrough, scrolling README detail or a physical demonstration. Inspect playback, not only a thumbnail: a file named `.mp4` may still be a motionless hold. Record the useful action's **source in/out times**, what visibly changes, when the result becomes readable, and whether the shot can fill the intended final duration. Preserve enough handles to choose a beat-aligned edit without losing the result.

Prioritize the first 3–5 seconds when allocating the strongest assets. Give the editor several relevant ways to see the hook: an action, a tight detail and a wider/result view where available. Build diversity from different source types, views, regions, scales and actions; do not merely collect multiple nearly identical screens. Search for clips that can work full-screen as well as split-screen. Record whether the important action and source context survive a vertical crop. Full-screen moving B-roll is a preferred option whenever it improves visual impact or clarity.

Keep a static original when it provides stronger proof than available motion. Attach a proposed slow zoom/reframe and the detail that must stay visible; a useful still with deliberate camera motion is better than irrelevant video. A captured still does not become evidence of real app interaction when animated. If a genuine recording cannot be obtained, use the honest still treatment or an identified illustration and keep that limitation in the asset index.

For each selected visual, add a short `motion_note` in its existing notes field (or the source shortlist): `kind` (recorded action / camera move on still / intentional still / authored illustration), `visible_action`, `usable_source_range`, `vertical_crop_limits`, and `suggested_layout`. These are editorial notes, not new required renderer keys. Mark opening candidates and reject repetitive or motionless clips that offer no stronger proof.

## Music and effects are production assets

Source the instrumental bed while sourcing B-roll. **Samin requires background music by default unless he explicitly opts out for this reel.** First inspect the user's reusable licensed library and already authorized media provider; then search an appropriate rights-cleared source or create an original instrumental with an available authorized generator. Choose an energetic rhythm with clear accents, enough usable duration, and room for the speaking voice. Record local file/hash, source or generation receipt, reuse basis, duration, intended musical in-point, observed beat/section markers and any required attribution. Measure tempo only when it helps editing; do not invent BPM from a title.

Select SFX for the actual actions: distinct clicks/typing, a sweep for a directed reveal, and a stronger impact for a real hook/payoff. Retain source/license information. Inspect and listen to their useful bounds; long silence before a sound causes a mistimed accent even when its file starts on the cut. Incidental audio from product demos stays muted unless explicitly chosen and cleared as part of the mix.

If a provider fails, check the documented error and make one specific retry when appropriate, then use another available authorized source, a verified local licensed track, or an original authored/generated instrumental. Do not spend outside existing authorization or claim a queued generation is an asset. If all viable routes fail, record `music.status: "blocked"`, the failed dependency and next action in `creative-review.json`/`operator-state.json`; continue independent editing and deliver only a clearly labelled incomplete preview until a playable music file is obtained. **Never silently replace the required music-backed output with voice plus SFX.**

## Reject noun matches before editing

An authentic page is not automatically a useful visual. Match the **action or relationship**, not just a word in the narration. “An AI judge weighs the arguments and decides” needs a visible evaluation relationship, relevant documented mechanism, actual example, or clear weighing/verdict metaphor. A Wikipedia definition of a courtroom judge does not show that process. A generic GitHub homepage does not show a repo's feature. An unrelated tweet mentioning AI does not support this tool's result.

Before selecting a shot, record these four answers in its asset request:

1. **Focal detail:** name the exact thing the viewer will recognize or read in the proposed crop, without needing the caption to explain why the page is there.
2. **Connection:** explain how that detail shows this beat's action/relationship. If it only repeats a noun, reject it.
3. **Alternative:** compare one stronger treatment, such as a mechanism diagram, actual resource excerpt, recorded action or simple physical metaphor. Prefer the one with the clearest immediate takeaway, not the most official-looking page.
4. **Phone check:** inspect the presentation crop at the planned on-screen size. Read the required words, or identify the visual action. If you cannot, tighten/change the crop or replace the shot before rendering.

The first lower-tier trial failed these checks: it inserted a whole Wikipedia Judge page for an AI evaluation beat, and an INVESTOR title/question card for a business-evaluation beat. Both files rendered correctly; neither provided the intended concrete visual explanation. Preserve that distinction. For an investor metaphor, a concise financial action/asset is more useful than a second text summary. For evaluation, a relevant source diagram can explain the mechanism, but must not imply this particular prompt was executed.

Do not keep a source just to satisfy an asset quota. A strong presenter beat or clearly identified illustration is better than irrelevant “proof.” Generated metaphors are allowed when useful; fabricated evidence is not.

## Capture a public page

Create `sources.json` from URLs you have read. This is a real example from the Council source family, not a requirement to use this repository in other stories:

```json
[{"id":"sdk-readme","url":"https://github.com/anthropics/claude-agent-sdk-python"}]
```

```bash
node production/capture_evidence.cjs --sources /absolute/sources.json --out /absolute/work/REEL/capture-01
```

The tool uses a disposable Chrome profile and captures original page content, overview, HTML and relevant README/heading crops with hashes. For a specific heading, add `"heading":"Exact visible heading"`; inspect `production/evidence-capture.md` for multiple headings. It does not log into Eden/Drive/X, prove a live product run, record scrolling, or validate facts. Open the resulting PNGs and the manifest. Reject a login wall, blank screenshot, collapsed section or crop that misses its useful text.

For an authenticated post or app, use the connected browser/appropriate CLI. Read the available browser tool instructions first; discover its actual tab/app state. Keep unrelated notifications, personal messages and account details out of the capture. Preserve the original private master separately; make a deliberate cropped/redacted presentation asset when needed. Record redaction as such; never alter the substantive claim.

## Capture a real action

Write a five-line recording brief: **start state, exact input, action, expected observable result, stop state**. Prepare the smallest harmless example that demonstrates the script. Record the app itself at readable resolution. Pause roughly half a second before the action and at least one second after the result, giving the editor trim handles. Make deliberate cursor movements; hide unrelated windows and notifications.

An API transcript or a recreated HTML composer is not a screen recording. If browser recording is unavailable, capture honest before/after screenshots and cut between them, or label the authored explanation. If the request needs genuine interaction proof and no recording can be made, keep that shot unresolved; do not claim execution.

If a recorded action takes 20 seconds but the line lasts three, preserve the action and result, remove dead waiting with a visible cut, then hold the result. Do not silently retime a measured benchmark or imply its sped-up footage shows real elapsed time.

## Download, trim and index

Prefer the connected Drive download or the source's provided download. Download an actual direct media URL returned by a tool/source, not a guessed CDN path. Record source URL, time/date, original filename, reuse basis and bytes/hash. An HTML error page renamed `.mp4` is not a video: probe and decode it.

For an inspected local clip, this is the ordinary extraction shape. Replace IN and LENGTH with measured seconds and CROP with actual source pixels; omit the crop filter when unnecessary. Re-encode the small selected excerpt, mute its incidental audio, preserve the master.

```bash
ffmpeg -ss IN -i /absolute/master.mp4 -t LENGTH \
  -vf 'crop=WIDTH:HEIGHT:X:Y' -an -c:v libx264 -crf 18 \
  -pix_fmt yuv420p -movflags +faststart /absolute/work/REEL/selected-clip.mp4
```

Keep enough usable duration for the entire intended shot. Freeze a final frame only when it is an intentional still hold; do not hide a too-short clip or loop an app result. Source in/out refers to the master; timeline start/end refers to the final reel. Keep those fields distinct.

Each selected asset needs: stable ID, local path, hash, source URL/master ID, capture/generation method, source bounds/crop if derived, representation, supported claim, limitations, reuse basis, and inspected status. Keep alternatives in the source shortlist; the active asset index must name what is actually rendered. `production/pilots/council-v2/asset-index.json` and `proof-sources.json` show the distinction.

For giveaways, link an original public resource with attribution or create an original guide/adaptation within its terms. A saved bookmark is not permission to redistribute a paid/private file. Show the actual final promised resource at the CTA, then keep its hash tied to the Skool/ManyChat handoff.
