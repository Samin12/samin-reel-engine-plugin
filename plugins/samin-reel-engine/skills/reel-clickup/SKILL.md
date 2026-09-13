---
name: reel-clickup
description: Turn a supplied reference link or existing reel package into ClickUp reel cards with scripts, research, giveaways and accurate workflow stages; use computer use when requested.
---

# Reel ClickUp

Build a usable production board, with the actual content inside each card. A title and a collection of empty placeholders are not a completed handoff.

Read [card and resource templates](references/card-template.md) when preparing content. Read [computer-use workflow](references/browser-workflow.md) before changing ClickUp through its UI. This folder is self-contained: it can be copied as a standalone skill or used inside Samin Reel Engine. No API key, renderer installation or private voice corpus is bundled or required for board population.

## Resolve this request

Identify the reference/source link, destination ClickUp List or Board, requested number of scripts, number of completed giveaways, and requested stages. Reuse destinations and decisions already supplied in the current conversation. If the destination is genuinely missing, ask for the List/Board link while preparing the content. Do not infer a destination from a public example or another account’s IDs.

Follow the requested count. With only a new link and no batch count, prepare one reel. “Five scripts, two in Built Resource” means five distinct scripts: finish two matching giveaways and put those two cards in Built Resource; keep the other three in Script. Select the two strongest resource opportunities unless the user chooses them. This does not mark any script approved, filmed or published.

“Use computer use” means make the ClickUp changes through the available browser/native-app tools. Do not silently replace those actions with REST, shell HTTP, Playwright outside the provided computer-use runtime, or hidden page APIs. Local writing, file checks and source research can use their appropriate tools. If computer use is unavailable, finish the local package and report the missing capability; ask whether an available API route is acceptable only if needed. When no interaction method was requested, a connected purpose-built ClickUp tool is also suitable.

## Inspect the link and existing work

- For a reference reel, inspect its actual transcript or accessible media. Prefer Eden when its tools are available; reuse a matching saved read. Record the origin and whether the transcript and any analysis were actually read. Separate your structural interpretation from tool-provided analysis. If only a caption is accessible, do not pretend it establishes the spoken hook. Continue research and label style matching provisional, requesting the transcript only when necessary.
- For a product/repository link, read its original documentation. Treat it as the subject, not automatically as the writing-style reference.
- For existing work, locate the script, research, giveaway and final files before regenerating anything. Preserve the recorded script. Do not rewrite spoken claims in the task as though they were in the finished video.
- Inspect existing target-list cards before creating new ones. Match on subject, reference link, keyword and presenter variant; do not duplicate a card just because its title differs slightly.

## Write in the resource-reel shape

For a new batch using Samin’s curated-resource format, each reel covers **one viewer outcome through several complementary resources**. Five scripts means five outcomes/stacks, not one tool per script. The [selected design reference](https://www.instagram.com/p/Dc7hhAUEvu1/) demonstrates the structure; verify its transcript before claiming to match its exact delivery.

1. **Hook:** lead with what the viewer can do, a familiar tool/task and an honest count.
2. **Named beats:** “First is…”, “Then there’s…”, “Third…”, “And finally…” as useful. Give every resource a distinct job and a concrete input, action or payoff. Call a mixed set of skills, CLIs and MCPs “resources” or “tools”.
3. **Concrete use:** connect the stack to a recognisable example, such as checking a booking form or producing a sourced comparison brief.
4. **CTA:** one uppercase keyword and the exact promised list, guide or prompt pack.

Aim initially for about 140–175 spoken words, then adjust to the reference and user. Keep clean spoken copy separate from links and editor notes. Use supplied voice samples when available; do not invent a personal-use story. A new reference may call for a different format—follow that request rather than forcing a five-item list.

Research every factual resource beat through current primary sources. Record name/type, direct URL, distinct job, first setup action, expected input/output, material access requirements, test status and a concrete visual to capture. Do not inherit old “all free”, performance, novelty or income claims from a reference. Reading documentation is different from running the complete stack.

When the Reel Engine checkout is available, use its `skill/scripts/check_script.py` and `tools/hold-your-voice/hold_voice.py` on the clean scripts. Otherwise count words and review the structure locally; do not install the video-rendering stack merely to populate a board. Compare advisory voice flags with the actual reference.

## Build the requested resource packages

For each card requested in Built Resource, create the **complete promised giveaway**, not just a plan to write it. Include all named resources in script order, direct legitimate links, documented setup/first actions, access requirements, an original copyable prompt or useful checklist when promised, and a concrete output target. Mark unexecuted setup as documented, not tested.

Prefer a readable native ClickUp Doc plus a downloadable local copy. A ZIP is useful when the giveaway includes separate prompts or worksheets. Link to third-party tools and paid materials; distribute only the original guide or material whose reuse is authorised. A local source list suffices only when the CTA promises a list.

For cards staying in Script, include the researched links and a clearly labelled giveaway specification. The draft CTA can name the intended resource, but record that delivery packaging is still pending. Do not represent it as ready to send.

## Populate and stage the cards

Use the card template’s fields: **Script, Research, Resource, Build / reverse-engineering notes, Filming notes, Final edited reel, Next step**. Put the complete spoken script directly in the description and attach a clean copy when supported. Link the actual resource Doc and files. Use observed UI copy-link actions for new native Docs and task URLs.

The requested workflow is:

**Script → Approved → Built Resource → Filmed → Edited → Published**

Reuse matching existing statuses, including harmless case differences. Create missing stages only within the authorised target; preserve unrelated statuses and cards. Group the Board by Status. A stage label describes the workflow state and is not evidence that an earlier approval happened.

| Stage | Basis |
|---|---|
| Script | Written draft with research and an honest resource plan |
| Approved | Actual user/team approval recorded |
| Built Resource | Requested giveaway exists, opens and matches the CTA |
| Filmed | Actual recording is linked or attached |
| Edited | Actual finished edit is linked or attached; playback/approval limits remain explicit |
| Published | Verified published reel URL, not a file upload or GitHub release |

Follow explicit user staging instructions when supported by the artifacts. If the requested status would misrepresent missing work, explain the precise gap and keep the card at the supported stage. Never fabricate a final video to fill a field.

Create Samin/real-person and Avatar variants **only when requested**. Keep the script identical if requested, add the matching tags, link shared docs, and attach each version’s own final video. If the avatar edit does not exist, leave its final field pending; do not relabel the human video as an avatar edit.

## Verify before reporting completion

Reopen every created/updated card and its relevant Doc. Confirm the list, status, visible full script, resource links and attachment filenames. Check that hook count, spoken names, numbered visuals and giveaway entries agree. Read the Board and confirm the requested grouping and number of cards.

After a timeout or uncertain save, inspect the list/card before retrying. Keep a small local receipt with card/Doc URLs, statuses, attachment names, resource hashes and unresolved items so a resumed run can continue without duplicates. Never put credentials or private production files into a public repository.

Return concise task links with stages and which giveaways are complete. Report anything left blocked. Board population does not publish Instagram/Skool content, enable ManyChat or send DMs; do those only when separately requested.
