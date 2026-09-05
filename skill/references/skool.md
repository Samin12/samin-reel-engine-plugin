# Turn each giveaway into a Skool resource

Stage four produces the resource, a Skool-ready post and its ManyChat delivery handoff. The reel's keyword, the post's promise and the downloadable or linked material must describe the same thing.

Resolve the destination from the current task and live account/community state. AI Answers and Claude Club both exist in Samin's context; that does not identify which one this batch belongs in. If the target remains ambiguous, prepare the drafts with `target_community: null` and ask for the community when that choice is needed. Do not select one from an old memory or a similar name.

## Draft the member experience

For every selected reel, write a short title and member introduction, a clear list of what the resource contains, and one practical first action. Link the source authors close to borrowed facts or referenced tools. Read any Eden item before incorporating it, retain its saved provenance internally, and follow the reuse decision in `saved-resources.md`.

Create `skool/drafts/KEYWORD.md` and `skool/handoff.json`. Each handoff entry should carry `reel_id`, `keyword`, title, draft path, asset path/hash, source attribution and any inspected Eden references. Include a short optional classroom description when the resource is useful enough to retain in a course/resource library; do not create a course merely because a one-off post exists.

Record community access separately from the resource's access: free, paid, membership/login required, or unconfirmed. Avoid promises that a viewer can open the resource until the intended audience's access is checked. Draft placeholders identify missing destinations; they are never evidence that hosting or posting happened.

A saved resource can also become a bonus community guide without a new reel. Keep it in a separate `bonus_resources` handoff list, retain its saved-item and source provenance, and leave reel/keyword enrollment unset. Adding that guide must not silently add a ManyChat trigger or imply that it informed earlier scripts.

## Record publication and delivery separately

Keep `native_post_url` null and status `draft_not_posted` until the post is actually published and reopened successfully. “I post it in my Skool community” describes the user's workflow; it is not a request to publish this batch immediately.

When posting is requested, confirm the selected community, resource access and working attachment/link, then perform and verify the authorized action. Store the real post URL and any classroom location. A ManyChat button may deliver that Skool URL when the target audience can access it. If membership or payment is required, disclose that in the reel/DM instead of implying immediate free access.

For the current example packet, resolve `project_root` from `references/project-location.json`, then read `runs/2026-09-04/skool/handoff.json`. A completed draft package and live giveaway delivery are separate states.
