# Populate ClickUp with computer use

Use the computer-use tools actually available in the current Codex task. Read their entrypoint documentation before operating. Tool names, browser IDs, element references and open tabs are session-specific; never copy coordinates or IDs from an old run.

## 1. Confirm the destination

Open the user’s List/Board link using the requested browser or authenticated native ClickUp app. Keep verification browsing in the background when supported. Read the Space/List name and current board before editing.

If sign-in is required, use the normal authorised login route or let the user finish it. Do not request an API token when the user chose computer use. Continue preparing the scripts/resources while sign-in is pending. If no UI control is available, report that specific missing capability rather than claiming the board was updated.

Inspect existing cards by title, keyword, reference URL and variant. Reuse a match when the user is continuing it. Keep unrelated cards, assignees, due dates, tags and documents unchanged.

## 2. Set up only the requested workflow

Select Board and inspect its grouping. Choose **Status** when needed. Reuse the existing stage names and order:

`Script → Approved → Built Resource → Filmed → Edited → Published`

If the user requested this workflow and a stage is missing, use the target List’s status controls to add it. Avoid editing a shared Space status set when that would change unrelated Lists; use a List-specific override where available. If the UI cannot isolate the change, explain the actual affected scope and ask only for the unresolved choice.

Do not rename or delete existing custom statuses merely to make the board resemble an example. Existing tasks in later stages stay where they are.

## 3. Create the resource Docs

Finish the local resource content first. Create a named Doc in the intended List/location through ClickUp’s **Create Doc / Add view → Doc** control, using whichever the live UI exposes.

Paste through the editor’s supported Markdown/rich-text flow. Inspect the resulting headings, numbered items, links, prompt blocks and tables. A successful paste is not proof that the rich-text conversion preserved the content.

Use the Doc’s **Copy link** action and retain that observed URL. Follow the destination’s normal workspace access; do not enable internet public sharing as part of board population. ClickUp’s workspace-visible “public” Docs and external public sharing are different controls. If a private Doc is unavailable on the plan, use an ordinary workspace Doc for the authorised non-sensitive guide, or attach the finished guide directly to its card. State the actual format used.

When a native Doc cannot be created, a readable finished `.md`, `.pdf` or `.docx` attachment is a valid fallback. Do not upgrade the plan or alter account permissions to force a Doc. Do not call a local file a native ClickUp Doc.

## 4. Populate each card

Create one card per requested reel or presenter variant. Use the actual title and the completed description from the card template. Prefer entering the content in a single coherent paste, then verify that the full script and sections survived.

Use the observed status selector for the supported requested stage. Add Samin/real-person or Avatar tags only when that versioning was requested. Do not add arbitrary assignees or dates.

Attach the clean script and useful research/filming document. For completed giveaways, attach the guide and optional toolkit ZIP, and link the native Doc near the top of the card. For already edited work, attach the actual final MP4 and identify the version. If uploads are restricted, use an existing authorised, working file link; do not invent a URL or upload a tiny placeholder.

Read the computer-use tool’s file-upload instructions before using its file chooser. Use the provided chooser/attachment workflow; do not simulate an upload with a filename string or mutate the page’s hidden state.

After each UI mutation, read fresh visible/accessibility state before choosing the next target. If save/creation times out, search or reopen the target before retrying. Resume missing content or attachments rather than creating another card or Doc.

## 5. Verify the saved result

Open each affected card after saving and check:

- Correct List, title, status and any requested presenter tag.
- Complete spoken script with the chosen hook and CTA.
- Resource link opens the actual guide with all promised entries and prompts.
- Attachment list shows the intended filenames; open the resource and any final video when relevant.
- Pending work is stated accurately; no invented approval, test or publication.

Return to the Board and confirm the new cards in the requested groups. For a five-script/two-resource batch, verify three new cards in Script and two new cards in Built Resource. Other existing cards do not count toward that batch total.

Capture observed task/Doc links and stages in the local receipt. End with those links and a concise completion statement. Do not perform unrelated posting, messaging, automation setup or permission changes.
