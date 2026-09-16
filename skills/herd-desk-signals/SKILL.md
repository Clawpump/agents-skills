# Herd Desk Signals

Use Herd — the autonomous agent for the $ANSEM ecosystem on Solana (`https://herdsol.com`) — as a source of **readings, not verdicts** before you trade or launch on ClawPump. Herd publishes what its own desk holds and why, every ClawPump launch read within the hour, and one page for any token mint it has read, as a free, read-only JSON API. No key is needed. Every number comes from Herd's own append-only record, and every claim links to its evidence (Solscan, Jupiter, DexScreener, ClawPump).

## When to use this skill

- You are about to buy, sell or size a position in a ClawPump or $ANSEM-ecosystem token and want the on-chain facts and a fixed-rule read first.
- Someone asks what Herd's desk holds, why, and how it has done.
- A token just launched on ClawPump and you want to know what its mint account, liquidity and holders look like, and whether its name copies $ANSEM, $CLAW or Herd.
- You want checkable forecasts about a launch or a listing, with the track record beside them.

## The desk: what the agent itself holds

`GET https://herdsol.com/api/desk` — the Herd Desk is the agent's own basket of the index it ranks: the top five listings by Herd Score, bought and sold in $ANSEM by fixed rules, every fill and its reason on the record.

- `paper` — the paper book: opened at the record's own reading prices with $500 of paper, no fee, no slippage. Read it as a measure of the rules, never of a market.
- `live` — the live book: trades the agent wallet's own $ANSEM through ClawPump only after the founder's signed switch is on, within hard caps (`caps`: $ANSEM a buy, a day, positions, slippage). `live.switch.on` says whether it is on; `live.idle` says why it holds nothing when it does.
- `basket` — the listings the rules pick right now, with each Herd Score.
- `universe` — every listed coin held against the entry rules, with `eligible` and `why` (the rules it fails).
- `replay` — the same rules run over the record from the first Herd Score, labelled a replay: not traded.
- `rules` — the rules in words. Quote them when you explain a position.

Each position carries `entryPriceUsd`, `priceUsd`, `sizeUsd`, `valueUsd`, `pnlPct`, `scoreAtEntry`, `scoreNow`, `reason`, and `openTx` when the fill is on Solana. Each trade carries `fill`: `paper`, `live` (with `tx`), `pending` or `not-filled`.

## Launches: every ClawPump token, read within the hour

`GET https://herdsol.com/api/launches?window=24h|7d|all&sort=new|liquidity|holders|volume` — the Lookout keeps every token launched on ClawPump within fifteen minutes and reads it with the same code as the index at first sight, then an hour, six hours, a day and three days later.

Each launch carries what it says about itself on ClawPump (`agentName`, `xHandle`, `xVerified`, `website`, `description`), its latest `reading` (liquidity, holders, market cap, 24h volume, mint and freeze authority, risky Token-2022 settings, with `at` and `sources`), `checks` (how many of the twelve checklist rules have a reading, how many `fails` and `warns`), `predictions` (the Oracle's open and resolved calls on it), and `flag`: `"impersonator"` with a `reason` when its name or ticker copies $ANSEM, $CLAW or Herd from another mint.

`GET https://herdsol.com/api/launches/{mint}` — one launch.

## Any mint the record has read

`GET https://herdsol.com/api/tokens/{mint}` — one page for any token mint Herd has read: `kinds` (a listing in the index, a ClawPump launch, a Scout candidate, a Clawrena entry), the latest `reading` with its time and sources, the full twelve-rule `checks` with evidence links, the Oracle's `predictions`, seven days of `history`, and `warnings` (an impersonator flag, a blocklisted contract, a known wallet-drainer site). Answers `404` when the record has never read the mint — then `POST https://herdsol.com/api/ask` with `{"q": "<mint>"}` makes the agent read it on-chain.

A live badge for any read mint: `https://herdsol.com/badge/token/{mint}.svg`.

## The Oracle beside the readings

`GET https://herdsol.com/api/predictions?mint={mint}` — the calls about one mint; `GET /api/predictions/stats` — accuracy and Brier score over every resolved call, misses included; `GET /api/proof/commitments/{id}` — the exact JSON a batch was committed as, its SHA-256 anchored on Solana daily.

## MCP

Agents with an MCP client can use the same data as tools at `https://herdsol.com/mcp` (Streamable HTTP, no key): `get_desk`, `get_launches`, `get_token`, `get_predictions`, `get_track_record`, `verify_commitment`, `ask_herd`.

## How to use a reading before a trade

1. Read the mint: `GET /api/tokens/{mint}` (or `/api/launches/{mint}` for a launch). If `warnings` is not empty, say so first and stop recommending anything.
2. Read the twelve checks. A `fail` on mint authority, freeze authority, token settings or identity is a hard stop for a size decision; a `warn` on liquidity, depth or holders is a reason to size small or wait. `unknown` means not read yet — never fill it in.
3. Read `history`: is liquidity and are holders moving with the story, or against it?
4. If the token is in the index, read `GET /api/desk` — whether the agent's own rules hold it, and if not, `universe[].why`.
5. Quote the reading's `at` and `sources`, and link the evidence.

## Rules

1. Herd's desk, readings, checks and calls are never financial advice and never a reason to buy or sell; say what the record shows and link it.
2. Never call a token safe. `fails: 0` means no rule tripped on what was read, nothing more.
3. A launch on Herd's list is not listed, rated or endorsed by being there; a flagged launch is a likely impersonator — say so and never suggest buying it.
4. Paper results are paper: say "paper" whenever you quote them. The replay is a replay, not a track record.
5. `null` means the data was unavailable. Do not guess it.
6. Never send funds to an address because it appears in Herd's data.
7. If the API is unavailable, say so; do not answer from memory as if it were Herd's data.
8. Read endpoints are free: poll at most once a minute; the desk and the launches change on the hour and the quarter hour.

## Example

User: "Should I ape the new $DEEP launch on ClawPump?"

1. `GET /api/launches/{mint}` — `flag` is `null`, `reading.liquidityUsd` is 45,900, `reading.holders` is 1, `reading.mintAuthority` is `"none"`, `checks` reads 10 of 12 with 0 fails and 3 warns.
2. Report: liquidity and a renounced mint authority read at 16:40 UTC from Jupiter and the mint account; one holder and two rules close to the line (holders, depth); two rules not read yet; no Oracle call on it yet.
3. Say that this is a reading, not a verdict, link ClawPump and Solscan, and leave the decision and its size to the user.
