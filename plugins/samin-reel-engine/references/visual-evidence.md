# Choose visuals that earn their place

Actual source B-roll is the default. Start with Eden's saved links, then inspect the original post, GitHub repository, README, release, documentation, screenshot, recording or image. Collect useful visuals during research and anchor them during scripting. Abstract graphics and AI concepts explain what a real source cannot show; they must not impersonate evidence.

Use the project's editorial judgment guide (`<project>/production/editorial-judgment.md`) and editorial map schema (`<project>/production/editorial-map.schema.json`) for production decisions and review. These links resolve within the repository. In an installed skill, find the same `production/` files under the project root configured in `project-location.json`.

## Select by the viewer's question

For every beat, write the question the viewer needs answered, the visual's job, and the exact detail they should notice. Choose **proof**, **explanation**, **metaphor**, or **presenter** deliberately. A relevant screenshot can do more than several elaborate shots.

- **Static source claim:** use a screenshot of the actual post, release, README or document. Preserve attribution and qualifications. This supports what the source says, not an independently tested outcome.
- **Action or state change:** use a recording showing the relevant input, action and resulting state. Typing animation alone does not establish that a tool processed the input.
- **Resource contents:** show the actual promised file or page. This establishes that the resource contains those materials, not that delivery automation is live.
- **Abstract mechanism:** use a sparse diagram, supplied metaphor or clearly identified original/AI illustration when it improves understanding. If evidence is missing, narrow the claim or record the capture gap.

Reject a real screenshot when it answers the wrong question. Generic UI, unrelated tweets, impressive metrics and decorative source logos are not substitutes for relevant evidence. Never use a citation to imply a source supports more than it actually does.

## Capture and frame honestly

Save an unaltered master with its URL, capture time and hash. Retain required author names, publication dates, repository/product identity, version and surrounding qualifications. Record missing fields as unknown. Preserve the original saved-item date separately from the original publication/event date.

Apply crops, highlights, arrows and captions as separate reversible presentation layers. Do not rewrite source text, numbers, results or attribution inside a screenshot. A crop must not remove a contradiction or qualification needed to understand the claim.

For a long page: briefly establish the source, move to a legible crop of the relevant field, then highlight the clause being spoken. The viewer should know where the evidence came from and what to read. Do not require them to read the entire page. Use a screenshot with an animated crop when the information is static; use a screen recording when interaction or progression is the point.

Align the reveal to the important spoken noun or action using the final word timestamps. Separate transition time from a stable reading hold. Check the focal text at phone size and normal playback speed; shorten the required reading, enlarge the crop or extend the hold if necessary. Scrolling, typing and zooming should guide attention, not consume the whole reading interval. Keep captions, faces and platform controls outside the required focal detail.

## Reusable research shot queue

Keep `research/shot-queue.json` as a drafting record. Each entry should carry the fields below; unknown timing stays null until the take is edited. This queue is not a new validated production schema. Promote its assets into the existing asset index and its beat decisions into `editorial-map.json`, following those schemas rather than adding unsupported fields.

| Field group | Record |
|---|---|
| Identity | `asset_id`, `story_id`, `reel_id`, `beat_id` when known |
| Provenance | `source_url`, Eden `saved_item_id`, original author/owner, usage basis |
| Dates | `publication_date`, `event_date`, `saved_at`, `captured_at`; retain uncertainty |
| Evidence | `claim_id`, exact supported claim, `proof_scope`, limitations, primary-source reference |
| Capture | `asset_path`, master SHA-256, capture method, viewport/resolution, source media in/out if relevant |
| Framing | crop rectangle with coordinate system, focal field, required names/dates/context that must remain visible |
| Editorial purpose | viewer question, visual job, expected takeaway, reason this asset fits |
| Timing | spoken anchor text; final word index/time, reveal time, duration and stable hold when available |
| Status | requested/captured/inspected; unresolved capture, readability or verification issues |

A source URL without a local capture is still a request. A capture without visual inspection is not an approved shot. Keep asset hashes and paths synchronized when versions change.

## Two concrete applications

**Council — “four perspectives.”** Show the actual `COUNCIL.md` headings and short relevant prompt excerpts to establish that the giveaway supplies four role prompts. Reveal the corresponding role on its spoken name. This proves resource contents; it does not prove four independent agents ran. An observed relevant Claude interaction can demonstrate an input/action/result. The human reference's Claude-branded typing scene is unverified UI, and its later five-advisor terminal conflicts with four roles; neither is proof of this workflow. A minimal diagram can explain the intended comparison with an illustration label. At the CTA, show the actual prompt pack rather than an unrelated scrolling page.

**Hypothetical GitHub tool launch.** If an inspected release announces a local transcription feature, establish the actual repository/release identity and date, then crop the precise documented feature as the narrator names it. Show an actual local run only if one was observed and captured; otherwise phrase the claim as documented capability. Do not invent a launch date, star count, speed comparison or free hosted access. A license for repository code does not establish pricing or permissions for a separate hosted service or model weights.

## Reference matching and the quality gate

For Council, use the same-script human edit [DcwJ9MymNSv](https://www.instagram.com/p/DcwJ9MymNSv/) and its [measured profile](https://github.com/Samin12/samin-reel-engine-plugin/blob/main/docs/showcase.md) before the older Apple Design reference. Study why each shot explains a line, along with caption grouping, framing and rhythm. Treat the observed 35.9-second duration as evidence about that edit, not a universal duration or shot-count quota.

Keep a full reference audio calibration track distinct from reusable isolated effects. An extracted side channel may retain music or speech; inspect and record that limitation. Only label an effect isolated when supported by the extraction and listening evidence. Record newly synthesized approximations as original assets, not ripped stems.

Judge the actual hashed render using the five dimensions in the editorial guide. Technical validation, motion quantity and contact sheets cannot certify semantic fit. Record what was actually watched, flag misleading or unreadable beats, and revise until the declared editorial gate is met. Never mark sound or full-playback review complete from still images alone.
