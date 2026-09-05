---
name: reel-deliver
description: "Build matching reel giveaways and Skool/ManyChat handoffs, package verified review exports, and update the existing production queue."
---

# Reel delivery and giveaways

Resolve `<plugin>` as the directory containing this plugin's `.codex-plugin/`. Run `python3 <plugin>/scripts/reel.py context` to find the configured project; pass `--project /absolute/checkout` **before** `context` when a project was supplied. Treat every `production/...`, `voice/...` and `runs/...` path as relative to that project. Shared references are linked below; load only this stage's instructions. Keep credentials and large working media out of the plugin cache.

Read [Skool](../../references/skool.md), [ManyChat](../../references/manychat.md), and `<project>/production/delivery/README.md`. Use the existing authorized destinations and current state; do not recreate the project or infer a public URL.

Build the exact promised resource. Use relevant inspected Eden saves with attribution and appropriate reuse, or create an original guide/prompt pack. Verify its contents and hash. The CTA, keyword, resource title and delivery copy must agree. Show the real resource in the edit.

Prepare the Skool post and resource handoff, then the ManyChat opening interaction and delivery-link packet. Keep missing resource URL, native post URL or reel selector null. The current API adapter can inspect metadata and prepare packets; sending an existing flow is not creating an Instagram comment automation. Use the real app configuration workflow when live publication/setup is requested.

For a review delivery, package the MP4, editable metadata, source/asset index, actual giveaway, review receipt and optional comparison player. Upload large exports to the existing private release and verify server size/hash. Commit the plugin/runtime/instructions to the existing local project repository. Keep keys, private download URLs and large raw filming masters out of Git.

Update the relevant existing Multica records with the verified release/version and observed review status, preserving unrelated work. A repository release does not publish Instagram/Skool or deliver ManyChat DMs. Only mark those states live after actual configured state and the authorized test/publication is observed.
