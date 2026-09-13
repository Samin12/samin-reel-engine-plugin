# Turn a new link into a complete ClickUp reel workflow

Copy a prompt below into Codex and replace the reference and ClickUp links. Codex needs working computer-use tools and access to your ClickUp account. This page does not install a browser connection or supply credentials.

The reusable [Reel ClickUp skill](../plugins/samin-reel-engine/skills/reel-clickup/SKILL.md) contains the full workflow. Its [card template](../plugins/samin-reel-engine/skills/reel-clickup/references/card-template.md) and [computer-use instructions](../plugins/samin-reel-engine/skills/reel-clickup/references/browser-workflow.md) travel with it.

## Repeat the five-script, two-resource batch

```text
Read and use this skill, including its two linked references:
https://github.com/Samin12/samin-reel-engine-plugin/blob/main/plugins/samin-reel-engine/skills/reel-clickup/SKILL.md

New reference reel: PASTE_REFERENCE_LINK_HERE
ClickUp List or Board: PASTE_CLICKUP_LINK_HERE

Use computer use to populate ClickUp. Create five distinct reel scripts in the reference’s hook and writing style. Each reel should cover one specific viewer outcome through a complementary stack of useful plugins, skills, MCPs or tools. Inspect the actual reference transcript and verify new factual claims with primary sources.

Choose the two strongest giveaway opportunities, build their complete resource docs and downloadable packs, and put those two tasks in Built Resource. Put the other three in Script, with the remaining giveaway work clearly stated.

Use this workflow: Script → Approved → Built Resource → Filmed → Edited → Published. Reuse the existing List, stages and matching tasks; preserve unrelated work.

Each card must contain:
- The complete spoken script directly in the description.
- Research: source links, supported claims, access requirements and what was tested.
- Resource: actual Doc and files when built, otherwise the exact remaining resource plan.
- Build/reverse-engineering notes explaining how the reference was adapted.
- Filming notes: what to show for each resource beat and the CTA.
- Final edited reel if an actual matching export exists; otherwise mark it pending.
- One concrete next step.

Match every keyword, resource name and hook count to the giveaway. Reopen the cards and docs and verify the board groups, scripts, links and attachments. Return the five task links and their stages. Do not publish reels or send DMs.
```

## Just one new reel

```text
Use the Reel ClickUp skill:
https://github.com/Samin12/samin-reel-engine-plugin/blob/main/plugins/samin-reel-engine/skills/reel-clickup/SKILL.md

Reference or subject: PASTE_NEW_LINK_HERE
Destination: PASTE_CLICKUP_LIST_OR_BOARD_LINK_HERE

Use computer use to create or update one complete reel card. Write the script, research its claims and build the exact resource promised in the CTA. Include the script, research, resource Doc/download, adaptation notes and filming notes. Put it in Built Resource once the giveaway exists and opens. Attach an existing matching final edit only if one is available. Verify the saved card and return its link.
```

## Package existing human and avatar edits

```text
Use the Reel ClickUp skill:
https://github.com/Samin12/samin-reel-engine-plugin/blob/main/plugins/samin-reel-engine/skills/reel-clickup/SKILL.md

Existing reel files/project: PASTE_PROJECT_PATH_OR_LINK_HERE
ClickUp List or Board: PASTE_CLICKUP_LINK_HERE

Use computer use to create or update two cards: Samin (real person) and Avatar. Keep the same existing spoken script in both, add the corresponding tags, link the shared research and resource docs, and attach each version’s own final edited MP4. Put both in Edited only if both edits exist; report any missing version. Preserve the actual recorded script and avoid regenerating completed work. Reopen and verify both cards, then return their links.
```

## What each card looks like

**Script** — full spoken copy, word count and estimated timing.

**Research** — original links, claim evidence, access limits and test state.

**Resource** — the real guide/list, copyable prompts or checklist and download.

**Build / reverse-engineering notes** — observed reference structure and the new adaptation.

**Filming notes** — relevant source/demo for each spoken beat and capture state.

**Final edited reel** — the actual matching export, or an honest pending state.

**Next step** — the next production action.

## Optional: install the standalone skill

Copy the entire `plugins/samin-reel-engine/skills/reel-clickup/` folder—including `references/` and `agents/`—into your Codex skills directory, commonly `~/.codex/skills/reel-clickup/`. Start a new task so Codex can discover it, then invoke `$reel-clickup` with your links. An existing installation should be updated deliberately rather than overwritten blindly.

The link-based prompts work without installing the whole video-rendering environment. Local/API/script checks and an actual computer-use run are different verification levels; the skill does not bundle an authenticated ClickUp connection.
