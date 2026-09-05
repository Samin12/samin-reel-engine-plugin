# ManyChat asset delivery stage

The pipeline ends with a concrete giveaway handoff for each chosen reel: the viewer comments its keyword, receives an opening DM, taps its quick reply, and gets the promised resource. Build the resource before writing delivery copy. Keep its name, scope and contents consistent with the spoken CTA.

Read the run's `reel-manifest.json` and finished `assets/` files. Write `manychat/handoff.json` plus a short `manychat/SETUP.md`. The JSON is an internal handoff, not a ManyChat export or directly importable automation.

## Required packet fields

Preserve the manifest's canonical `id` as `reel_id`. Include `keyword`, `asset_title`, run-relative `asset_path`, absolute `asset_local_path`, nullable `asset_url`, and nullable `post_id_or_url`. Keep a content hash so a reviewer can identify the resource version.

Draft three resource-specific `public_replies`; one `opening_dm` with text and a quick reply; and a `delivery_dm` with text and a resource button. Mirror the delivery copy into `message_text` for validation. The trigger must select the corresponding specific reel. Never insert a fabricated reel identifier or placeholder website as a real destination. Quick Automation supports specific-reel targeting and up to three public reply variants. [Official setup documentation](https://help.manychat.com/hc/en-us/articles/16654065283100-Quick-Automation-Auto-DM-links-from-comments).

Use a single opening private-reply content block and route its quick-reply interaction to delivery. Do not use an unconditional opening-node continuation. Receiving the first DM does not itself opt the viewer in; an Open website action does not establish that interaction either. [Official trigger documentation](https://help.manychat.com/hc/en-us/articles/14281316989724-Instagram-Post-and-Reel-Comments-trigger).

## State and completion

Set `status: draft_not_configured`, `live_test.status: not_run`, and reminders disabled initially. Keep email collection and follow gates disabled unless that campaign requests them. Unanswered opening messages receive no automatic follow-up.

A complete draft handoff contains real copy and existing resources even when hosting and reel selection remain pending. Live delivery additionally requires a verified public asset URL, the actual reel, account configuration and a recorded successful end-to-end test. Save those facts separately; never infer them from a completed document or a reachable product page.

When no ManyChat connector or account surface is available, finish the handoff and identify the missing live destinations. Do not mark it deployed. For an example, resolve `project_root` from the skill's `references/project-location.json`, then read `runs/2026-09-04/manychat/SETUP.md` beneath that root. Adapt every new batch's keywords, resources and copy.
