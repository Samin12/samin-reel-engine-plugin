# Samin Reel Engine

Turn a real, demonstrable story into a reel Samin can film, then edit his supplied footage into a finished video. Before filming, deliver the spoken script with sources, visual requirements and the promised resource. After filming, deliver the actual rendered MP4 plus its editable timeline, indexed assets and giveaway handoff.

**Actual source B-roll comes first.** Collect original posts, relevant GitHub README/release crops, documentation, screenshots, recordings and images while researching. Choose each shot for the viewer's question and the specific spoken claim it explains or supports. More shots, faster motion and abstract diagrams do not compensate for irrelevant evidence. Read [visual-evidence.md](visual-evidence.md) when selecting stories, writing visual beats or editing.

## Four-stage pipeline

**Research → Ideation → Scripting → Giveaway assets.** Research starts with Samin's Eden saves and adds fresh primary sources. Stage four includes a Skool resource post and the ManyChat delivery handoff. Every stage saves a reusable artifact for the next stage. A user may run the whole pipeline or resume at any stage whose inputs exist.

| Stage | Input | Saved output | Ready when |
|---|---|---|---|
| Research | Eden saves, window, audience, prior story ledger | `research/saved-resources.json`, `research/story-bank.json`, evidence, visual index and shot queue | Saved contents were read; chosen claims and dates have primary-source support; useful source visuals were inspected or capture gaps recorded |
| Ideation | Verified story bank and voice examples | `ideation/ideas.json` and `ideation/ideas.md` | Each selected idea has an angle, hook options, keyword and deliverable promise |
| Scripting | Selected idea and matching voice samples | `scripts/*.md`, `reel-manifest.json`, checks, anchored shot queue | Clean spoken copy matches the idea, voice and evidence; visual beats identify what viewers should see and why |
| Giveaway assets | Final script's literal CTA and inspected saved resources | `assets/<KEYWORD>.md`, `skool/drafts/`, `skool/handoff.json`, `manychat/handoff.json` | The promised resource, Skool post and matching delivery copy are prepared |

Use `python3 <skill>/scripts/pipeline.py init --run <run>` to create stage directories without replacing work, and `status --run <run>` or `validate --run <run>` to inspect saved stage readiness. This helper checks the artifacts; the agent performs research, ideation and writing. It does not silently run language-model jobs. Read [pipeline-contract.md](pipeline-contract.md) when starting or resuming a batch.

Keep local pipeline completion separate from distribution readiness. A finished asset and ManyChat setup packet can exist before its public URL and specific reel are assigned. Do not mark an automation live without seeing its configured state and a delivery test.

## Find the voice project

Use a project explicitly supplied by the user; otherwise read `references/project-location.json` for the local project containing `voice/samples/`, `voice/voice-profile.json`, and previous runs. When `project_root` is null in a checkout, resolve `project_root_relative_to_skill` from the directory containing this SKILL.md. `tools/install-skill.py` writes the current checkout's absolute root into the installed copy. This is a personal skill; keep the corpus in that writing project, outside plugin folders. If the configured project moves, rerun the installer or locate the supplied corpus before claiming a voice match.

Read [voice-guide.md](voice-guide.md), then three samples that fit the requested reel type. The linked September Reels board is the primary voice reference. The samples are evidence of style, not proof that their tools, income claims, performance figures, or publication status are true. Use [templates.md](templates.md) for a starting shape; vary the opening and sequence to fit the story.

## Stage 1 — Research

Default to the last 30 inclusive calendar days ending today and five scripts unless the request suggests otherwise. State the date window once. Use a `runs/YYYY-MM-DD/` folder in the writing project; preserve previous drafts when rerunning.

First read [saved-resources.md](saved-resources.md). Search Samin's Eden library for the topic and relevant bookmarks, and open the most useful saved items. Preserve item IDs, original source URLs, what you actually read, and the reuse decision in `research/saved-resources.json`. The 30-day limit applies to news, not useful evergreen bookmarks. A saved date is not a launch date. If Eden is unavailable, say so and record the limitation; continue the independent research below without claiming saved-resource access.

1. Run the bundled collector for GitHub discovery or named repositories:

   ```bash
   python3 <skill>/scripts/research.py --days 30 --as-of YYYY-MM-DD --out <run>/research/collect
   python3 <skill>/scripts/research.py --repo OWNER/REPO --days 30 --as-of YYYY-MM-DD --out <run>/research/collect
   ```

   Inspect its manifest, errors, candidates, and visual index. These are discovery leads, not verified claims. If a source fails, report the gap and continue with available sources. Do not execute candidate repository code.

2. Search official release posts, product changelogs, model cards, and original demos for the same window. Use available web search or Firecrawl. Social posts and Hacker News can reveal an angle; follow them to the underlying primary source. A changing feed, repository push, star count, or roundup date does not establish a launch date.

3. Open the primary sources of promising candidates. Record event date, publication date, access date, exact supported claims, qualifications, and visual URLs using [research-contract.md](research-contract.md). Follow Eden links to the original post, repository or document. Capture useful source visuals now, retaining author/date or repository identity and necessary context in the unaltered master. Start `research/shot-queue.json` using [visual-evidence.md](visual-evidence.md); a URL alone is a capture request, not a finished asset. If the window is thin, explicitly separate useful evergreen stories rather than invent freshness. Treat repositories created in the window as newly created repositories, not necessarily newly launched products.

4. Compare against the corpus and `<project>/story-ledger.json`. If that ledger is missing, create it from observed source references and prior run manifests; do not infer publication. Distinguish reference/filming, drafted, accepted, and published. A prior draft is not a shipped story; a new release or genuinely different mechanism may justify a new angle. Rank by a visible payoff, clarity of mechanism, evidence, audience fit, and freshness. Stars and social metrics alone are insufficient.

5. Select the requested batch and proceed to drafting. The user's request to develop examples authorizes the full local workflow; a routine idea-selection pause is unnecessary. Save rejected leads and why they failed.

## Stage 2 — Ideation

For each promising story, propose two or three genuinely different hook angles. Select one using viewer usefulness, the visual demonstration, evidence strength and fit with the source corpus. The recommendation can be made autonomously unless the user requested a selection pause.

Save a selected idea with a stable `id`, `story_id`, `selected: true`, archetype, angle, hook options, selected hook, uppercase keyword, sample anchors, script path, and a giveaway object containing its title, local path and exact CTA promise. Save rejected/deferred ideas with their reason. Design the giveaway here so the script has a real next step; build the final asset after the script's promise is settled.

Match each giveaway to relevant Eden saves before inventing a new resource. Record `saved_resource_ids` and choose whether to link the original, summarize with attribution, adapt with permission, or create an original worksheet. An empty match list is valid when the saved collection adds nothing useful. Do not force unrelated bookmarks into an existing script.

## Stage 3 — Scripting

- Most standard samples run 98–195 whitespace-counted words. Use roughly 140–175 as a starting target; choose the nearest matching sample over a rigid quota. The short promotional sample is a separate format.
- Write one spoken beat per paragraph. Keep stage directions, source citations, timings, and factual caveats for the editor outside the script, except qualifications needed for the spoken claim to remain true.
- Prefer concrete viewer actions: give it this input, connect this tool, compare this output. Name the thing early. Explain the mechanism before the payoff.
- Use observed vocabulary naturally; do not scatter “basically,” “actually,” or “literally” to simulate a voice. Do not invent personal use, results, popularity, income, free access, or “just launched.”
- A useful number is optional. Retain energy through specificity when no defensible statistic exists.
- Beside the clean script, attach each visual beat to a viewer question, visual job, inspected source asset, exact spoken noun/action, and required reading hold. Use a screenshot for a static source claim and a recording when the action or state change matters. Keep unsupported behavior out of both narration and imagery; use clearly identified explanation or illustration when no relevant evidence exists.
- The comment-keyword ending is typical for this corpus. Carry the selected idea's keyword and promise into the CTA. Do not promise a tested setup or a recorded video unless one exists. Save `idea_id` in the reel manifest so the result can be traced through the pipeline.

## Stage 4 — Giveaway assets, Skool and ManyChat

Build the actual resource the script offers: useful steps, a copyable prompt/file, a curated list, or a link to an existing video. A source list is sufficient only when that is what the CTA promises. Check every link and distinguish documented instructions from a setup you actually ran.

Use the inspected Eden references where they improve the resource, retain attribution, and keep paid/private source material out of distributable files. Read [skool.md](skool.md). Create a matching Skool post draft with a title, member introduction, resource contents and one practical first action. Record the exact community, audience access, asset hash and eventual native post URL in `skool/handoff.json`; unknown destinations stay null. The user posts resources in Skool, so this draft is part of every full run. Prepare an optional classroom description when it helps members find an evergreen resource again.

Read [manychat.md](manychat.md). Create one setup packet per selected reel: exact keyword, specific reel selector, public reply variants, opening private DM and interaction button, delivery DM and asset button, local asset path and public delivery URL, and test status. Keep optional reminders off unless requested. This is an operator handoff, not a claim that arbitrary JSON can be imported into ManyChat.

Use an existing user-supplied hosted asset URL when available. When the asset is not hosted, preserve `asset_url: null` and an explicit hosting task; never substitute a local path or a source homepage for the promised giveaway. Prepare the complete local packet before requesting any needed hosting/account decision. If the user requests live setup, inspect the connected ManyChat account or UI, assign the intended reel, test the exact keyword and link, and enable only the authorized automation. Creating this pipeline alone does not send messages.

A verified Skool post can be the ManyChat destination when the intended viewer can access the resource. Disclose membership/payment requirements in the delivery copy. A local Skool draft is not a public URL or a published community post. Posting and delivery are separate observed states.

## Check before handoff

1. Map each factual sentence back to the story bank. Recheck mutable access, pricing, licensing, and compatibility close to filming. Keep model weights, hosted products, SDK code, and paid inference distinct.
2. Run `python3 <skill>/scripts/check_script.py <spoken-script.md>` for words, beats, hook length, and estimated duration. Timing is a planning estimate until Samin records a read-through.
3. Run the project's local Hold Your Voice helper: `python3 <project>/tools/hold-your-voice/hold_voice.py scan --format json <spoken-script.md>`. For flagged lines, use `rewrite-prompt --profile <project>/voice/voice-profile.json <spoken-script.md>`, revise the actual weak lines, and rescan. A flag at line 0 is a document-level diagnostic, not a literal line to replace. Compare it with source samples, then record a keep or revise decision. One sentence per beat is common in this corpus; do not distort it just to silence a generic paragraph flag. Keep a factual product name even when the vocabulary scanner flags it. The scanner detects writing patterns; a clean scan does not prove a voice match. Compare with two source samples by hand.
4. Save a filming document containing the spoken scripts, evidence links, words/timing estimates, the source-backed shot queue and matching resource paths. Each planned shot needs a reason, readable focal detail and capture status; unresolved capture requests remain explicit. Preserve clean individual scripts for filming and mechanical checks. Use Roughdraft when the user wants review/comments; wait for Done Reviewing, then read the edited file and address CriticMarkup.
5. Record the new files as drafts in `<project>/story-ledger.json`. Only accepted user revisions can update the profile. Preserve original and accepted versions first. Keep profile evolution local; do not add cloud sync, posting, messaging, recurring jobs, or public publication to this workflow without a user request.

## Filming intake and final video production

For real source B-roll, run `node <project>/production/capture_evidence.cjs --sources sources.json --out <new-capture-directory>` after collecting and reading the relevant URLs; read `production/evidence-capture.md` for the input contract. It captures original public pages and README regions in a disposable browser and saves provenance. Inspect each image before selecting it. Run `python3 <project>/production/check_editorial.py --map <pilot>/editorial-map.json` to catch broken beat/asset joins and stale render approval; this checks structure, not editorial truth or quality.

When Samin supplies a Drive recording or asks for an edited reel, read `<project>/production/WORKFLOW.md`, `production/editorial-judgment.md`, `production/editorial-map.schema.json`, and `production/editor/README.md`. Resolve these paths from the configured project root. The current primary Council reference is the human edit [DcwJ9MymNSv](https://www.instagram.com/p/DcwJ9MymNSv/), profiled in `production/reference/council-human/visual-profile.json`: 35.9 seconds of video, approximately 226 ASR-counted words/minute. It supersedes the older Apple Design reference for this same-script edit. Retain `production/reference/style-profile.json` as a secondary reference. The earlier four stages feed this production workflow; a script document is not the final deliverable for an editing request.

- Download the complete selected source recording, preserve its Drive ID, expected byte count and hash, then make a proxy and word-timestamp transcript. Keep large media and credentials outside Git. `production/download_ranges.py` supports verified resumption for authorized large media URLs; it never changes sharing or bypasses account access.
- Align the supplied scripts to actual takes. Inspect repeated phrases and false starts. Save source in/out points and retime captions with every cut. `production/prepare_take.py` applies an edit decision list and maps the words. Never invent a spoken line or replace Samin with an avatar.
- Promote the research shot queue into the asset index and `editorial-map.json`. Prefer relevant actual source B-roll, then a clearly bounded explanation; abstract or AI-generated imagery is a fallback for concepts. Record each asset's source, ownership/reuse, hash, capture method and proof limits. A README proves what its author documents; only an observed run can establish your demonstrated result. An unrelated real screen is still irrelevant evidence.
- Make every reveal answer the beat's viewer question. Anchor it to the important spoken noun/action, then allow a stable mobile reading hold. For long pages, establish the source, crop to the focal field, and highlight the relevant clause with a separate overlay. Preserve unaltered masters, required names/dates and context; never crop away a contradiction. Use typing, scrolling, crop changes, purposeful SFX and restrained VFX to direct attention. A shot-count target or decorative motion cannot replace this judgment.
- Use the primary reference's measured layout, caption grouping and phrase rhythm while preserving intelligibility. Match actual cuts and word timing rather than imposing a blanket speed multiplier. Keep reference audio used for calibration separate from isolated reusable effects. Record extraction method and inspect speech/music residue before calling a clip isolated; label synthesized approximations as original. Exact font or effect identities require evidence.
- Build and render with `production/editor/edit.py`. HyperFrames is HeyGen's local HTML/GSAP renderer; this path uses the original filmed speaker without a paid avatar-generation job. Inspect the actual rendered video, captions, motion, sound, complete decode and timing before handing it over. Apply the editorial judgment rubric to the hashed render: semantic fit, evidence honesty, timing/readability, composition/focus and reference/voice. Record revisions for weak beats; successful rendering and contact sheets do not establish editorial quality. Keep project, timeline, source/take mapping and render hash together.
- Prepare the matching resource, Skool draft and ManyChat publication packet. Inspect the existing broad keyword flow before adding a trigger. Read `production/delivery/` for supported API operations and the app configuration step. Never commit API keys. A future publish request authorizes the named publication workflow; preparing a pilot does not itself publish it or send DMs.

Use the existing Multica reel project when authenticated. Update its specific production/pilot task to reflect observed state, preserve unrelated completed tasks and leave unrequested jobs unassigned. The queue points to the repository and assets; it does not replace the source manifest or evidence.

## Typical deliverables

`research/saved-resources.json`, `research/story-bank.json`, `research/visual-index.json`, `research/shot-queue.json`, `ideation/ideas.json`, `scripts/*.md`, `assets/<KEYWORD>.md`, `skool/drafts/`, both delivery handoffs, a combined review document, and a receipt listing what was read, verified, drafted, and left untested. Editing adds the asset index, `editorial-map.json`, timeline and inspected render. Keep sources and samples private unless the user asks to share them. The current `pipeline.py` checks the four core stage joins and ManyChat fields; separately inspect visual evidence, Skool paths, asset hashes, attribution and access before calling the full handoff complete.
