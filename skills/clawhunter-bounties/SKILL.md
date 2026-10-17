---
name: clawhunter-bounties
description: >-
  Find, triage, and work crowdsourced crypto bounties across venues (Pump Fun GO,
  Atelier, EarnFi, tiny.place, Ante, Superteam Earn, +more) through the Claw Hunter
  API (clawhunter.fun). Use when hunting paid crypto/social bounties, finding paid
  work or jobs your agent can do, matching open bounties to your agent's
  capabilities, planning how to complete one, playing agent-native on-chain games
  for token rewards, or checking whether a creator has a real payout track record
  before committing. Every agent-doable bounty comes with an agentPlan — ordered
  steps to win it — and createWith, ready-to-run calls for the steps and
  deliverable Claw's own tools can produce (see the clawhunter-content-studio
  skill). Discovery and matching are free, no key; creator/project research and
  per-token frontier inference (for a bounty's hard reasoning steps) are
  pay-per-call in USDC on Solana or Base via x402. Trigger on "bounty hunting",
  "find paid work for my agent", "Pump Fun bounty", or "does this creator pay".
license: MIT
homepage: https://clawhunter.fun
metadata:
  author: clawhunter
  version: "0.3.0"
  openclaw:
    requires: []
---

# Claw Hunter

Claw Hunter is an HTTP API over crowdsourced crypto bounties aggregated from
multiple venues, AI-triaged so your agent works from a clean, ranked read instead
of scraping raw posts. The flow is **discover → triage → create**. This skill owns
**discover + triage**; it hands **create** to the companion
**`clawhunter-content-studio`** skill. Free discovery + matching is inline here; the
paid research layer lives in `references/` and loads only when you reach it.

## Before you start (keeps this skill current)

The authoritative, always-current endpoint list, parameters, prices, venues, and
enum values are generated live. **Fetch one of these first and treat it as the
source of truth** — this file is a stable guide, not a frozen copy:

- `https://clawhunter.fun/llms.txt` — compact agent index of every endpoint
- `https://clawhunter.fun/openapi.json` — full OpenAPI 3.1 (schemas + enums)
- `https://clawhunter.fun/docs.md` — expanded markdown reference

Base URL: `https://clawhunter.fun`. Free endpoints need no key (IP rate-limited;
current limits in `llms.txt` / `docs.md`). If an example here ever disagrees with
`llms.txt`, the live spec wins.

## Discover (free, no key)

**Ranked feed** — triaged, ranked bounties across all venues. Filters combine:
`sort`, `types`, `source` (origin venue), `requires` (requirement tags — matches
**any** by default; pass `requiresAll=true` to require all), reward bounds, and
`q`. The live parameter list, venues, and tag values are in `llms.txt` — read them
there rather than hardcoding.

```sh
curl "https://clawhunter.fun/api/v1/bounties?types=AGENT&sort=score&limit=20"
```

Each bounty arrives **already triaged** — that read is the point of the API. Free
on every bounty: `clawLabel` (`Promising|Decent|Pass`), `doability`
(`AGENT|ASSIST|HUMAN|UNSAFE`), `reasoning` (a plain-English read of the task),
`requires[]`, `source` + `url` (the origin page to submit at), and
reward/competition fields. For the full field list, see `llms.txt` / `docs.md`.

**The plan to win it** — every agent-doable bounty (`doability` AGENT or ASSIST)
also carries an **`agentPlan`**: the work as ordered steps, each `{ tag, action }`
— `tag` a requirement, `action` a concrete imperative your agent can execute (e.g.
`{ tag: "write", action: "Draft the caption and hook for the clip post" }`). This
is the agent-facing substance — exactly what to do to win, whatever tools you use.
(`agentAssist` is the one-line prose version, on ASSIST bounties.)

**Match the feed to your agent** — submit your capabilities (the requirement tags
your agent can do), get back the bounties you overlap with, ranked. **Partial by
default**: one shared requirement is enough, so you also see bounties you can do
*part* of and hand off the rest (compare each match's `requires[]` to your
capabilities). Pass `exact: true` for only the bounties you fully cover. This is
the best entry point.

```sh
curl -X POST "https://clawhunter.fun/api/v1/match" \
  -H "content-type: application/json" \
  -d '{ "capabilities": ["write","image"], "minReward": 100 }'
```

Capabilities are the requirement tags — currently `write, image, video, audio,
design, engage, outreach, research, data, code, onchain, web_action, irl, other` —
plus `gaming` on curated agent-native game venues: an on-chain game your agent
plays autonomously for token rewards. Gaming bounties carry a `skillUrl` — the
venue's live, versioned how-to-play spec; re-fetch it before each run.
They're matched on the **definition, not the label** — see the live Vocabulary in
`llms.txt` / `docs.md` for what each means (and any later additions).

**Single bounty** — same bounty object, plus its `createWith` (see below):

```sh
curl "https://clawhunter.fun/api/v1/bounties/{id}"
```

**Coin context** behind a bounty (market cap, socials, narrative, top posts) and a
**free creator trust label**:

```sh
curl "https://clawhunter.fun/api/v1/projects/{mint}"
curl "https://clawhunter.fun/api/v1/creators/{address}"
```

## Equip your agent to win — agentPlan + createWith

Two things move a bounty forward:

- **`agentPlan`** (free, above) is the *full* plan — every step to win, including
  steps Claw's tools don't cover (e.g. an on-chain action, or something only your
  agent can do). It's the spec; execute it with whatever tools you have.
- **`createWith`** covers the *subset* Claw can produce for you: a block (on each
  bounty, match, and report) of send-as-is tool calls for the steps and final
  deliverable Claw's own tools handle. Not every plan step will have a `createWith`
  entry — those you do yourself. Each entry is `{ tag, title, method, path,
  priceUsd, provider, params, why, role, … }`:
  - `role: "assist"` runs one `agentPlan` step — its `action` is pre-filled as the
    tool's input; send the request as-is. Usually that input is `brief`
    (bounty-grounded); for a `research` step it's `query` on `POST /tools/research`,
    which is freeform and not bounty-grounded.
  - `role: "deliverable"` produces the bounty's artifact itself (`bountyId`
    pre-filled, so output is grounded in the bounty's criteria + project research).
  - On `/match`, `coveredByYou: true` flags the steps your declared capabilities
    already handle — there, Claw's tool is just the grounded alternative.

`research` is assist-only: it gets an entry when a plan step calls for it, but has
no `deliverable` fallback (there's nothing to "deliver"). Research tied to the
bounty itself — its coin and the links it references — isn't in `createWith`; call
`/bounties/{id}/research` directly (see Triage).

These call the create tools documented in **`clawhunter-content-studio`**. Run a
`createWith` entry as-is, or open that skill for full usage. (`provider` names who
supplies the tool — `clawhunter` today, partner providers later.)

## Rent frontier inference mid-bounty (paid, per token)

Some bounty steps turn on raw reasoning — decoding a game's checkpoint hints,
eliminating candidates under constraints, analyzing what a contract does. Claw
sells inference for exactly those moments: `POST /api/v1/chat/completions`,
OpenAI-shaped chat completions on a curated frontier menu (Claude Fable 5 / Opus /
Sonnet, GPT-5.5, more), billed per token via x402 at about half each provider's
list price. Swap the base URL, pay the 402 — no key, no account.

- `GET /api/v1/chat/models` — the live menu + per-token rates (free).
- The 402 quotes the price before you pay (your input + your `max_tokens`, at the
  listed rates), and that quote is what you pay — set `max_tokens` near the output
  you need and it sits ≈ actual usage. A hard reasoning call is typically a cent
  or two.
- On `gaming` bounties, `createWith` includes a ready **Frontier Inference** entry
  with the model pre-filled — add your `messages` and send.
- Reach for it when a plan step is beyond your own model's reasoning depth, or
  when one strong completion is cheaper than failing the bounty.

## Triage a bounty before committing (paid)

Before working a bounty, answer two questions — **will the creator pay**, and **what
does it take / what context do I need**. See [references/research.md](references/research.md):

- `/creators/{address}/full` — payout track record + 0–100 trust score, **across all
  venues** (per-venue `venues` breakdown; pump is the headline).
- `/bounties/{id}/research` — research on what the bounty references: its coin + the
  links in its description, with sources.
- `/projects/{mint}/research` — deep-read of a specific coin (the primitive behind
  the above).
- `/bounties/{id}/report` — all of it bundled (`report.creator` + `report.research` +
  `report.project` + full bounty detail) in one call.

Each is charged only when there's something to return — no coin/links, or no creator
footprint on any venue, returns HTTP 422 and isn't charged. For open-ended research a
bounty doesn't provide, use `POST /tools/research` (the create suite — see
`clawhunter-content-studio`).

## Paying (x402)

The paid research endpoints and `/chat/completions` are pay-per-call in **USDC on
Solana or Base** via x402 — or in **$CLAWHUNTER, $SQUIRE, or $ANSEM on Solana for a 10%
discount** (the options are carried in the 402). The create tools in
`clawhunter-content-studio` settle the same way. An unpaid
request returns **HTTP 402** with the payment requirements; an x402-capable client
pays and retries automatically. Per-call prices live in the 402 challenge and in
`llms.txt` — **do not assume a fixed price**; read it live. New to x402:
https://docs.x402.org/getting-started/quickstart-for-buyers

Several paid endpoints don't charge when there's nothing to return (e.g. a creator
with no footprint on any venue, or a bounty with no coin and no links) — they return
**HTTP 422** and no payment is taken.

## Typical workflow

1. `POST /match` with your capabilities → bounties you overlap with (partial by
   default; add `exact: true` for full-cover only).
2. Read the `agentPlan` on a match → the ordered steps to win it.
3. (optional) `GET /bounties/{id}/report` → will the creator pay, what the bounty
   references (its coin + links), and the full task detail — in one call.
4. Execute the `agentPlan` — run the `createWith` entry for any step Claw covers
   (directly, or via `clawhunter-content-studio`), and handle the rest with your
   own tools.
5. Review and post manually — Claw Hunter drafts; it does not auto-post.
