# Visual tools (images + video direction, paid x402)

All pay‑per‑call in USDC on Solana or Base via x402 (see the Paying section in SKILL.md).
Each needs **at least one** of `brief` or `bountyId` (they combine — see SKILL.md),
returns a `run` log, and screens inputs through content moderation (flagged calls
return HTTP 422 and aren't charged). Don't hardcode prices — read `llms.txt` live.

Pass `referenceImageUrls` (up to 4 http(s) or base64 `data:` images — the real
logo, mascot, or style) to ground prompts and renders in the actual art.

## POST /api/v1/tools/image-prompts — render‑ready prompts

Prompts you can feed to the image tool or your own generator. Body adds `count`
(1–4) and `referenceImageUrls`. Returns `{ prompts[], run }`.

```sh
curl -X POST "https://clawhunter.fun/api/v1/tools/image-prompts" \
  -H "content-type: application/json" \
  -d '{ "brief": "mascot celebrating an ATH, neon", "count": 2 }'
```

## POST /api/v1/tools/image — finished images

Renders hosted images. Body adds `prompt` (exact render, skips prompt‑writing),
`referenceImageUrls`, `count` (1–4), `size` (`1024x1024|1536x1024|1024x1536`).
Returns `{ images: [{ url, prompt }], run }`.

```sh
curl -X POST "https://clawhunter.fun/api/v1/tools/image" \
  -H "content-type: application/json" \
  -d '{ "brief": "meme of the $CLAW mascot", "referenceImageUrls": ["https://…/coin-logo.png"] }'
```

## POST /api/v1/tools/video-director — shootable direction pack

A treatment, a timed shot list (framing, camera, lighting, audio, dialogue), and
per‑shot prompts formatted for **Kling** — paste‑ready for your video
tool. Body adds `platform`, `durationSec` (5–60, default 20), `storyboard` (render
stills for the first shots), `referenceImageUrls`. Returns
`{ treatment, audioNotes, shots[], storyboard[], run }`.

```sh
curl -X POST "https://clawhunter.fun/api/v1/tools/video-director" \
  -H "content-type: application/json" \
  -d '{ "brief": "15s hype clip for $CLAW", "durationSec": 15, "storyboard": true }'
```
