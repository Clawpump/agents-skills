---
name: pumpdata
description: "Before an alpha call or a buy on pump.fun: the base rate for the market-cap band (how often coins like this one paid), what the buyers have been (winner, bot, supply seller, new), the deployer's record with how similar launches went, and an honest replay of a pick list with fees and fills. Every PumpSwap trade, ever. Read-only; paid per call in USDC over x402, from $0.005; yesterday's base rates free."
version: 1.1.0
author: pumpdatafun
tags: [solana, pump.fun, base-rate, wallets, deployer, replay, backtest, x402, mcp, data, risk]
platforms: [linux, macos, windows]
prerequisites:
  commands: [curl]
metadata:
  hermes:
    category: crypto
    requires_toolsets: [terminal]
    related_skills: [rug-check, survivor-check, clawpump, dex-pools]
    homepage: https://pumpdata.fun
---

# pumpdata — base rates, wallet records, launch records, replay

You can read pumpdata.fun, a warehouse of every PumpSwap trade ever and every pump.fun bonding-curve trade since
March 2025, read from the chain's own ledger with the dead coins kept. `rug-check` says whether a coin is safe to
touch; `survivor-check` says whether it has lasted; this says whether coins like it have ever paid, what its buyers
have been, what its deployer has done, and what a list of picks would really have made. Every call is a read, paid
per call in USDC over x402 with your own wallet, from half a cent. Nothing here signs a trade.

## Free, before any wallet

- `GET https://pumpdata.fun/public/baserate.json`: yesterday's base rate for every market-cap band, refreshed
  hourly, the same answer the paid call gives for that day. Read this first; pay only for another window.
- `GET https://pumpdata.fun/llms.txt` (what is in the warehouse), `GET https://pumpdata.fun/openapi.json` (the
  contract, with the price of each call in `x-payment-info`).
- Telegram: `/baserate 15k-28k` to @pumpdatafun_bot.

## When to use it

| you are about to | call | price |
|---|---|---|
| post an **alpha report** on a coin at $X market cap | `GET /baserate` for that band and window: "4.5% of coins at $15–28K reached 10x within 3 h this week" is the sentence that keeps the report honest | $0.005 (yesterday: free) |
| **buy** into a coin with N buyers | `POST /wallets` with the buyers' addresses: what they have been (winners, bots, supply sellers, fresh wallets) | $0.01 |
| trust a **deployer** or a fresh launch | `GET /launch/{mint}`: launches, graduations, the best run, the bundle, the insiders' share, and how launches that looked like this one at this age went over their next day | $0.005 |
| trust a **backtest**, yours included | `POST /replay`: the picks against the chain's history with fees, fills and the dead coins | $2 a run |

## The calls

Contract: https://pumpdata.fun/openapi.json. Docs: https://pumpdata.fun/llms.txt. Worked examples in curl, node and
python: https://github.com/pumpdatafun/pumpdata-examples.

| call | asks | answers |
|---|---|---|
| `GET https://pumpdata.fun/baserate?band=15k-28k&from=<iso>&to=<iso>&venue=any` | a market-cap band (edges snap to 5k, 10k, 15k, 20k, 28k, 40k, 60k, 100k, 250k, 1000k), a window of up to 31 days, `venue` any, curve or pool | `crossed` (coins with a crossing in the window, see Definitions), `reached` {2x, 5x, 10x, 20x} as shares within 3 h, `median_peak`, the window used |
| `POST https://pumpdata.fun/wallets` `{"addresses": [...], "mint": "<optional>"}` | up to 50 wallets, optionally the coin they are buying | per wallet: `class` (winner, bot, supply_seller, new, none), `pnl_sol`, `put_in`, `took_out`, `coins`, `first_seen`. The labels are rules, not opinions |
| `GET https://pumpdata.fun/launch/{mint}` | a mint | the deployer's record (launches, graduations, best run, gaps between launches), the bundle at creation, the insiders' share of supply, curve progress, and how launches that looked the same at this age went over the next 24 h |
| `POST https://pumpdata.fun/replay` `{"picks": [{"mint", "at", "size_sol"}, ...]}` | up to 500 picks, graduates only | `202` with a job id; poll `GET /replay/{id}` until `done`: what the picks made pick by pick and in sum, filled at the pool as it stood 3 s after the mark, pump.fun's fee by tier, 145,000 lamports a trade fixed, graduates that died in the sum; a pick still on the bonding curve fills nothing and comes back `skipped_not_covered` |

Definitions: a *crossing* is a coin's first trade with a market cap inside the band (a coin that jumps over the
band in one trade has none); the *peak* is the highest market cap, curve or pool, in the 3 h after; a window ending
under 3 h ago is cut at 3 h ago; USD is at the SOL price of the trade's hour. Every answer carries `X-Data-From`
(where the data begins) and `X-Data-As-Of` (the build it comes from).

## How to pay

x402 v2, USDC on Solana. A call without payment returns **402** with the offer (price, payee, network) in the body
and the `PAYMENT-REQUIRED` header. Sign the transfer with your wallet and retry with `PAYMENT-SIGNATURE`; the
answer comes back with the receipt in `PAYMENT-RESPONSE`. Your x402 tool does the retry for you. No key, no account.

**MCP:** the same calls as tools at `POST https://pumpdata.fun/mcp` (Streamable HTTP, JSON-RPC 2.0): `base_rate`,
`wallet_records`, `launch_record`, `replay`, `replay_result`. A tool called without `payment` returns the offer; call
again with the `PAYMENT-SIGNATURE` value as `payment`.

## What an answer means

| status | meaning | do this |
|---|---|---|
| `402` | the offer | pay and retry (your x402 tool does it) |
| `200` | the answer; nothing more to pay | quote the band, the window and `X-Data-As-Of` |
| `202` (replay) | queued, `id` in the body | poll `GET /replay/{id}` every few seconds until `status` is `done` |
| `404` `not_found` | nothing in that window | nothing was charged; ask a later window |
| `400` | the band or the window is malformed, or the window is over 31 days | fix it, or split the window into months |
| `429` | too many calls from one address | wait a few seconds |
| `503` `query_timeout` | the window took too long | narrow it and ask again |

## Rules

1. **Say the window.** Base rates move with the market; always quote the band and the window the answer used
   (`from` and `to` are echoed, clipped to coverage when needed, with a note).
2. **Say the as-of.** Quote `X-Data-As-Of` when the number matters; the archive trails the chain by hours.
3. **Dead coins count.** The shares are over every coin that crossed, including the ones that died. Never drop them.
4. **Never sign a trade from here.** This skill reads. Trades are your other tools, after the read.
5. **Spend small.** Yesterday's base rate is free; a window is half a cent; check one before spending $2 on a replay.
6. **Labels are rules.** A `winner` took out more than it put in over many coins; a `bot` trades like a machine; a
   `supply_seller` sold supply it was given. Say the label and the SOL behind it, not a verdict.

## Examples of expected behavior

The base-rate figures are real (the free file for October 16, 2026); the wallet, launch and replay figures show the
shape of an answer, not a real coin.

- **An alpha report on a coin at $20K.** Base rate, band `15k-28k`, yesterday, from the free file (October 16,
  2026): 2,059 coins crossed, 34% reached 2x, 11% 5x, 5.1% 10x, 2.0% 20x, median peak 1.46x. The report says: "Of
  coins that crossed $15–28K yesterday, one in twenty reached 10x within three hours; this call has to beat that."
- **A buy into a coin with 12 visible buyers.** `POST /wallets` with the 12 addresses and the mint. The agent reads
  the classes and the SOL: "7 new wallets, 3 bots, 2 winners; the winners have taken out 41 and 17 SOL net over
  their coins; no supply seller." Then it decides with its own rule, and `rug-check` for the contract.
- **A fresh launch from a known deployer.** `GET /launch/{mint}`: "This deployer's 9th launch; 2 graduated; the best
  ran 6.4x; a bundle of 4 wallets took 11% at creation; launches that looked like this at this age were dead within a
  day 83% of the time." Size accordingly, or pass.
- **A caller's "my picks did 40x".** `POST /replay` with the picks as posted (mint, time, 0.5 SOL each), poll the
  result, and report the sum with fees and fills and the dead ones, plus how many picks came back
  `skipped_not_covered` (still on the curve, not counted as wins or losses), next to the base rate for the same
  bands and window. If the replay is not above the base rate, say so.

## Output shape (base rate)

```
BASE RATE · $15–28K · 2026-10-16 00:00Z → 2026-10-17 00:00Z · as of 2026-10-17T18:01Z
crossed 2,059 · 2x 34% · 5x 11% · 10x 5.1% · 20x 2.0% · median peak 1.46x
```
