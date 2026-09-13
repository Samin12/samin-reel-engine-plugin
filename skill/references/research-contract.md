# Story and visual evidence

Use this compact record for each selected or rejected story. Fields can be null when genuinely unknown; unknown evidence cannot support a stronger claim.

For the default resource-stack format, one story is the shared viewer outcome and the complete ordered collection. Add the per-resource fields and reference breakdown described in [curated-resource-reels.md](curated-resource-reels.md); preserve the fields below for pipeline compatibility. Give each item's factual claim its own primary source instead of citing the reference reel as evidence for the whole stack.

```json
{
  "id": "short-stable-id",
  "title": "Specific event or tool",
  "status": "selected",
  "primary_url": "https://...",
  "event_date": "YYYY-MM-DD",
  "event_basis": "Official dated release entry",
  "publication_date": "YYYY-MM-DD",
  "retrieved_at": "ISO UTC timestamp",
  "freshness": "in_window",
  "claims": [{"claim": "Paraphrased supported fact", "source_url": "https://...", "evidence": "Brief support/location", "qualification": "Limits that change the claim"}],
  "visuals": [{"url": "https://...", "source_url": "https://...", "kind": "demo", "status": "linked_not_captured", "capture_note": "What the editor should show"}],
  "angle": "Viewer problem and visible payoff",
  "keyword": "WORD",
  "resource": "assets/WORD.md",
  "test_status": "source_verified_not_run",
  "decision_reason": "Why this is a reel or why rejected"
}
```

Freshness uses the event, not the retrieval timestamp. A model repository creation date supports “model repository appeared on this date”; use an announcement or release to claim a launch. If release evidence disagrees, preserve both and explain which event each dates. A commit after the requested end date cannot support a historical claim about what existed then.

Capture visual provenance: the real source page, exact image/demo link, what it shows, whether opened or captured, and any known usage terms. Repository code licensing does not automatically license every logo, screenshot, or third-party demo. Do not call a link a downloaded asset or call a recreated graphic an original screenshot. Use source material as filming references; resolve reuse rights for the intended publication if needed.

Preserve request failures and rejected stories. Silence is not evidence that a source had zero results. Keep source excerpts short, quote sparingly, and paraphrase facts in the scripts.

For every script, maintain a claim map in the editor notes or bank. A source-verified example can be filmed as a product explainer without claiming a personal test. If the script promises setup instructions, distinguish documented steps from executed steps in the resource.
