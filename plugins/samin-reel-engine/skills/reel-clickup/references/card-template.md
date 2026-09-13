# Card and resource templates

These are fillable structures, not text to paste with blanks. Replace bracketed fields with actual content; omit irrelevant optional sections or state the real pending work. Do not upload a template as though it were a finished giveaway.

## Task title

`KEYWORD — Specific viewer outcome`

For explicitly requested versions: `Subject — Samin (real person)` and `Subject — Avatar`. Preserve an existing meaningful title when updating.

## Task description

```markdown
# [KEYWORD] — [Reel title]

Stage: [Observed/requested supported stage]
Presenter: [Samin / Avatar / not selected]
CTA keyword: [KEYWORD]
Viewer outcome: [One concrete result]

## Script

[Complete clean spoken copy, one beat per paragraph. No source citations,
camera directions, HTML markers or headings inside the spoken copy.]

Length: [word count] words. Estimated [range] seconds at [assumed speaking rate].
Timing is unmeasured until recorded.

## Research

Reference: [Original reference link and transcript-read status]
Source check date: [Actual date]

1. [Resource name](original-source-url) — [Its distinct job and supported claim]
2. [Continue for every spoken resource, in the same order]

Evidence limits: [Material access requirements, unknowns and whether the
tools were documented, individually tested or tested as a complete workflow]

## Resource

[Resource title](actual-doc-link)
Download: [Actual attached filename or observed file link]
Contains: [Specific guide/list, prompts, checklist or worksheets]
Build state: [Complete / packaging pending, with the precise missing part]
Delivery state: [Hosted for intended audience / internal Doc only / not configured]

## Build / reverse-engineering notes

[What was observed in the reference: hook, resource order, transitions, CTA.]
[How this new reel adapts that structure and why its resources work together.]
[Actual artifacts built. Keep proposals separate from completed work.]

## Filming notes

| Beat | What to show | Readable detail / important action | Source | Capture state |
|---|---|---|---|---|
| Hook | [Concrete outcome and count] | [The one thing to understand] | [Basis] | [Actual state] |
| 1. [Name] | [Relevant source or demo] | [Specific noun/action] | [URL] | [Pending / captured] |
| CTA | [Actual giveaway] | [Title and useful excerpt] | [Doc/file] | [Actual state] |

## Final edited reel

[Actual playable MP4 attachment/link and variant, or “Not filmed/edited yet.”]
[Version, file identity and review limits when relevant.]

## Next step

[One concrete action that advances this card.]
```

Put the script high in the card so a creator can read it without opening an attachment. A source link or local path is not a replacement for the actual script. In ClickUp, use inline code for filename mentions such as `CLAUDE.md` to prevent unwanted domain auto-links; the attached spoken script should retain the plain words. Do not paste `SCRIPT START/END` HTML comments into rich-text descriptions.

## A complete giveaway Doc

Use this structure for the actual resource, filled with the selected reel’s content:

1. **Title and promise:** match the CTA keyword and deliverable exactly.
2. **Start here:** one concrete first action and the inputs the viewer needs.
3. **Ordered resources:** for each, name/type, original link, job, documented setup/first action, expected output and material access limits. Distinguish manual handoffs from connected integrations.
4. **Copyable prompt or checklist:** the actual usable text when promised. Include enough instructions for the viewer to produce a specific output; do not just say “ask AI to do it”.
5. **Worksheet/example:** include it if it makes the promised workflow usable. Label illustrative examples so they cannot be mistaken for observed results.
6. **Finish:** expected files/results and the checks that establish success.
7. **Provenance:** check date, original-guide attribution and what was or was not executed.

Suggested local package:

```text
run/
  scripts/KEYWORD.md
  research/KEYWORD.md
  resources/KEYWORD.md
  prompts/KEYWORD.txt          # when promised
  packages/KEYWORD-toolkit.zip # when useful
  clickup-receipt.json
```

Keep production data in the user’s workspace, outside the installed skill and public repository. A receipt should record the actual task and Doc URLs, status, attachment names, file hashes and pending items. It should contain no API tokens, cookies or unrelated account data.
