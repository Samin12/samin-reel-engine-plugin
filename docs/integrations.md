# Integrations

| Service or tool | Role | Included or required |
|---|---|---|
| Codex | Runs the eleven skills and stage tools | Plugin package included; Codex installation required |
| HyperFrames | Local HTML/video composition and rendering | Pinned npm dependency |
| FFmpeg / FFprobe | Media preparation, encode and audio checks | Install locally |
| Whisper | Word-timed local transcription | Optional intake dependencies and model file |
| GitHub / `gh` | Public-source research and versioned releases | Local CLI; authenticate when required |
| Eden / `edn` | Saved bookmarks and resource discovery | Use the agent’s available authenticated CLI/browser capability |
| Heptabase | Research board and script context | User-supplied export or available authorized capability |
| Google Drive | Filming-batch input | Authorized download or available connector; local files also work |
| Higgsfield / other generation tools | Missing explanatory images, motion or audio | Available provider capability and account; no bundled key |
| HeyGen | Optional provider route | Not required for local HyperFrames edits; not a bundled finished-edit adapter |
| Skool | Matching community resource/post handoff | Draft preparation; posting requires authorized app access |
| ManyChat | Comment-keyword/resource delivery handoff | Local packet adapter and optional metadata reads; no flow authoring or message sending in the adapter |
| Multica / ClickUp | Production status and handoff tracking | Use an available authenticated CLI/connector; no account provisioning |

Credentials stay in environment variables or owner-only files. The ManyChat adapter accepts `MANYCHAT_API_KEY` or an owner-only key file for its optional reads. It does not need a secret for offline preparation. Inspect its CLI before use; do not place keys in prompts, source files, README examples or release archives.

Provider availability, account permissions and API behavior must be checked at the time of use. A prepared packet is not a live automation; a successful API response is not proof that the intended person received the intended resource.
