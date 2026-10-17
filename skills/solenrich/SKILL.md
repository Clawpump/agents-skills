---
name: solenrich
description: "Solana onchain intelligence, pay-per-call over x402 with no API key: token due diligence with a SAFE/CAUTION/RISKY verdict, wallet risk and bot flags, smart-money and whale flow, memecoin entry and exit verdicts (runner-scan, trenches-check, exit-signal), cross-venue perps funding, StonkFun reward-coin gems and payout status."
version: 1.0.0
author: 0xSardius
tags: [solana, due-diligence, token-safety, smart-money, memecoin, perps, stonkfun, x402, analysis, risk, trading, defi]
platforms: [linux, macos, windows]
prerequisites:
  commands: [curl]
required_environment_variables: []
metadata:
  hermes:
    category: crypto
    requires_toolsets: [terminal]
    related_skills: [rug-check, whale-tracker, alpha-scanner, meme-analyzer, clawpump]
    homepage: https://solenrich.com
---

# SolEnrich — Solana Onchain Intelligence, Pay Per Call

SolEnrich turns raw Solana data into verdicts an agent can act on. It complements the ClawPump trade and
launch tools as the research step before `swap_execute` or a launch, and the monitoring step while a
position is open. **Read-only. Never signs a trade.** The agent pays USDC per call over x402 from its own
wallet; there is no account and no API key. 45 paid endpoints from $0.001 to $0.25, plus one free.

Base URL: `https://api.solenrich.com`. Every paid route is `POST /entrypoints/{key}/invoke` with a JSON
body. `format` is `json` (default), `llm` (a short deterministic briefing), or `both`.

## When to Use

- A user pastes a mint and asks "is this safe / is it a rug / can I ape this" → `due-diligence`
- Before `swap_execute` into any unfamiliar token → `trenches-check`, then `due-diligence`
- While holding a token → `exit-signal` with the entry price, no more than every 5 minutes
- "What's running right now" / "what are proven winners buying" → `runner-scan` / `smart-money-trenches`
- "Is this wallet a bot / risky / worth copying" → `enrich-wallet-light`, `copy-trade-signals`
- "Best venue for a SOL perp at $5K" → `perps-venue-comparison`
- "What's worth looking at on StonkFun" / "is this reward coin paying holders" → `stonk-gems`,
  `stonk-reward-risk`
- Any plain-English Solana question with an unclear intent → `query` ($0.003)

## How to Pay

Prefer, in this order:

1. **Pay.sh service** if the ClawPump platform lists SolEnrich under x402 services: recommend it, request
   the user's spending approval, then call through platform infrastructure.
2. **`pay curl`** from a terminal (Solana Foundation `pay` CLI handles the 402 challenge and returns
   the body):
   ```bash
   pay curl -X POST https://api.solenrich.com/entrypoints/due-diligence/invoke \
     -H 'content-type: application/json' \
     -d '{"mint":"<MINT>","format":"llm"}'
   ```
   Install once with `npm i -g @solana/pay`, create a wallet with `pay wallet create`, fund it with USDC
   and a little SOL.
3. **x402 client in code** (`@x402/fetch` + `@x402/svm`): wrap `fetch`, then call the same URLs.
   USDC on Solana or on Base, same price.

Free without any wallet: `GET /docs`, `GET /llms.txt`, `POST /demo/enrich` (10 per hour), and
`stonk-pairs`. Read `references/endpoints.md` for the full price list.

## Decision Table

| Intent | Endpoint | Price |
|---|---|---|
| Token safety with a verdict | `due-diligence` `{ "mint" }` | $0.02 |
| Cheap token read: price, liquidity, slippage, flags, transfer tax | `enrich-token-light` `{ "mint" }` | $0.002 |
| Wallet risk, holdings, bot flags | `enrich-wallet-light` `{ "address" }` | $0.002 |
| Does this wallet trade well | `copy-trade-signals` `{ "address" }` | $0.01 |
| Whales accumulating or distributing | `whale-watch` `{ "mint" }` | $0.008 |
| Fresh tokens accelerating now | `runner-scan` `{}` | $0.04 |
| Proven winners buying <6h launches | `smart-money-trenches` `{}` | $0.05 |
| Vet ONE candidate (velocity + smart money + attention) | `trenches-check` `{ "mint" }` | $0.03 |
| Should I exit | `exit-signal` `{ "mint", "entry_price_usd" }` | $0.04 |
| Best perps venue at my size | `perps-venue-comparison` `{ "market", "side", "size_usd" }` | $0.02 |
| Funding across Jupiter, Adrena, Flash, Hyperliquid, dYdX | `perps-cross-venue-funding` `{ "market" }` | $0.015 |
| StonkFun gems (early, real, paying) | `stonk-gems` `{}` | $0.03 |
| Is this StonkFun coin paying holders, tax cost | `stonk-reward-risk` `{ "mint" }` | $0.005 |
| What a StonkFun trade costs at my size, and whether payouts cover it | `stonk-quote` `{ "mint", "size_usd", "hold_days" }` | $0.005 |
| What to launch on StonkFun, against what | `stonk-launch-intel` `{}` | $0.02 |
| Plain-English question | `query` `{ "question" }` | $0.003 |

## The Trade Loop

Find → vet → size → hold → exit, about $0.09 to enter and $0.04 per exit check:

1. `runner-scan` or `smart-money-trenches` or `stonk-gems` — pick a candidate from the ranked list.
2. `trenches-check` on that mint — stop if `NO_SIGNAL`.
3. `due-diligence` — stop if `RISKY`. Never proceed past a `RISKY` verdict.
4. `enrich-token-light` — read `slippage_estimates` at the intended size and `transfer_tax.round_trip_pct`.
5. Confirm with the user, then the ClawPump trade tool.
6. `exit-signal` with `entry_price_usd` every 5+ minutes while holding — act on
   `position.net_pnl_after_exit_tax_pct`, not the gross figure, on taxed mints.

Every response has a `next_steps` array naming the next call.

## Presenting Results

Lead with the verdict and score, then the reasons, then the caveats. Example:

> 🟡 **CAUTION** — due-diligence risk 0.58. Top-10 holders own 44%, mint authority revoked, $1K trade
> costs 3.1% slippage. Whales neutral over 24h. _Caveat: Birdeye leg unavailable, holder count from RPC._

Always show the `caveats` array; it says which legs failed. Never present a verdict as advice, and never
execute a trade on a verdict without the user's confirmation.

## Rules

- Start with `-light` endpoints and escalate only when they flag something.
- Do not call `whale-watch` or `enrich-token-full` before `due-diligence`; it bundles them.
- Results are cached 30 s to 10 min server-side. Re-polling inside the window pays for the same answer.
- `trenches-check` and `exit-signal` unlock liquidity and holder deltas on a second call 5+ minutes
  later, not sooner.
- Field names are snake_case; addresses are base58 (Solana) except Hyperliquid endpoints, which take 0x.
- A 402 body lists every endpoint and price under `all_endpoints`; a 404 means an unknown key.
- Private keys stay in the local signer. SolEnrich never sees them.

## References

- `references/endpoints.md` — every endpoint with inputs and prices
- https://api.solenrich.com/docs — schemas and scoring methodology
- https://api.solenrich.com/llms.txt — one paragraph per endpoint
- https://github.com/solana-foundation/pay — the `pay` CLI
