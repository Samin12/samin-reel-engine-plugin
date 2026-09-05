# Generation recipes: fill a specific visual gap

Generate an illustration when real source material cannot clearly show an abstract idea, physical metaphor or useful connective shot. Capture the real source when the purpose is evidence. Do not synthesize an app interaction, tweet, README or test result and present it as observed behavior. A generated diagram may explain an architecture only when its relationships are correct and it is identified as an explanation.

## Choose the route

| Need | Route | Required check |
|---|---|---|
| A static explanation with exact words/arrows | Prefer authored HyperFrames/SVG/text from verified facts | Every label/count/arrow is correct and readable |
| A bitmap concept or background | Available image-generation tool; when using Higgsfield, its current GPT Image 2 route | Open the image before using it; no fake evidence |
| Consistent stylized role characters | Higgsfield Nano Banana 2 with an approved reference image | Same count, props, palette and identities across shots |
| Motion that adds meaning to an approved still | Higgsfield Seedance 2.0 image-to-video | Inspect start/middle/end and the exact selected interval for morphs, added objects or cuts |
| A real app click, typing or result | Screen recording/capture, not video generation | Actual input/action/output relationship |
| A short effect | Existing indexed SFX first; otherwise a supported audio-generation tool | Listen for speech/music residue, trim silence and mix under narration |
| Samin's presenter | Supplied filming footage | Do not replace him with an avatar or generate new spoken claims |

Provider names/defaults were checked against the available Higgsfield CLI on 2026-09-04. Read the installed provider skill and current schema before submitting; do not infer unavailable models or parameters. `production/providers/higgsfield-models-2026-09-04.json` records the checked shapes, not permanent availability. The connected Higgsfield tools and CLI have different upload contracts; follow the one actually being used.

## Local Higgsfield CLI path

1. Check `higgsfield account status`. Reuse an authenticated session. If authentication fails, the connected tool may still be available; otherwise record the missing login. Do not print or commit credentials.
2. Read the unfiltered model list once: `higgsfield model list --json`. Then inspect the chosen model with `higgsfield model get seedance_2_0 --json` or the relevant ID.
3. Write a prompt file and record the intended visual job, frame shape and acceptance checks. Submit one intentional job with `--wait --json` and preserve its returned job record. Local media paths passed to CLI media flags are uploaded automatically.
4. Inspect completed status and the actual result URL/file. A job ID or queued status is not an asset. Download only the returned output URL, then probe/hash it. Save prompt, model, reference image hash, job ID, source URL and selected trim in the asset index.
5. If output fails a concrete check, revise that specific prompt/reference and make one further attempt. Do not repeat a job after an uncertain timeout without first checking its ID/status. After two inadequate outputs, use a simpler authored explanation or presenter shot and record the limitation.

Use argument arrays so prompt punctuation cannot become shell code. For example, after validating the model/schema, this submits a new image job:

```python
from pathlib import Path
import subprocess
prompt = Path('/absolute/work/REEL/role-illustration-prompt.txt').read_text()
result = subprocess.run([
    'higgsfield', 'generate', 'create', 'nano_banana_2',
    '--prompt', prompt, '--aspect_ratio', '1:1', '--resolution', '2k',
    '--wait', '--json'
], text=True, capture_output=True, check=True)
Path('/absolute/work/REEL/role-illustration-job.json').write_text(result.stdout)
```

For a video, use `generate create seedance_2_0`, `--start-image /absolute/approved-image.png`, a motion prompt, `--duration 5`, an accepted aspect ratio/resolution, and `--wait --json`. Those parameter names were inspected; inspect current allowed values before changing them. Do not assume all providers accept the same flags. The B-roll track is muted by the editor: generated speech/music does not replace Samin's voice. Preserve a separately reviewed effect as its own asset if intentionally used.

The connector's scene-analysis path was tested on the exact Council v2 file: upload/confirm → `video_analysis_create` → `video_analysis_status`. Its sandbox upload path requires creating/exporting the file in the same remote sandbox call because that filesystem is temporary. Its attachment helper accepts user attachments, not arbitrary local workspace files. Prefer the authenticated CLI's local-file support when working in this desktop repository. Do not copy credentials into a remote sandbox to work around a file transfer.

## Write the visual prompt

Use this order: **job → subject/count → one action → composition/crop → reference consistency → exclusions**. Describe what should be visible, not the whole spoken script. Generate source material for the selected panel's aspect ratio. A top split at 1080×1920 with split fraction 0.4648 is about 1080×892; a tall full-screen image may crop badly there. Use a close supported ratio, keep important elements in the central area, and verify the final crop.

Example still prompt for an abstract four-role explanation:

> A simple pixel-art illustration explaining four distinct perspectives reviewing one idea. Exactly four characters, all fully visible: an advocate with a halo, a skeptic with a magnifier, an investor with coins, and a judge with a small gavel. All surround one central blank idea card. One coherent room, restrained warm lighting, clear silhouettes, ample separation. Match the supplied approved character reference and palette. Square composition with all essential subjects inside the central 80 percent. No extra characters, floating heads, decorative people, text, app interfaces, logos, statistics or captions. This is a conceptual illustration, not a product screenshot.

Example motion prompt after that still is approved:

> Preserve exactly the same four characters, identities, room and framing. The skeptic leans slightly toward the central card while the advocate turns toward them. One subtle camera push over five seconds; no cuts. Keep all four visible and the center unobstructed. Do not add characters, objects, text, dialogue, interface elements or new scenes. Finish with a stable composition that can be held.

Do not ask a video model to render the final captions or small UI text. Add those in HyperFrames after word timing is known. If the scene needs precise count or typography and the generator repeatedly gets it wrong, author it deterministically instead.

## Effect prompt and verification

Use existing sound assets before generating. If a supported audio model is used, request a narrow event such as “one short, dry paper flick with a soft high-frequency transient, no speech, music, reverb tail or ambience.” Provider schemas differ: the connector's speech tool may require a voice picker, so it is not automatically an SFX tool. Inspect current CLI/tool support; do not invent a voice ID or misuse speech generation.

Silence ASR does not establish a clean stem. Listen to the beginning, peak and tail, inspect duration/peak, then place the effect in context under the spoken line. Keep reference soundtrack, partial stereo-side excerpts, original synthesized effects and generated effects as different provenance categories. Council v2 used the full authorized reference mix; it did not demonstrate a clean reusable SFX separation.

Generated files are eligible only after inspection. Record wrong counts, changed identities, unintended letters, visual discontinuities, audio residue, unusable framing and the chosen repair. Do not mark a generation successful merely because the provider returned a URL.
