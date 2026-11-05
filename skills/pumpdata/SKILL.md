---
name: pumpdata
description: "Before an alpha call or a buy on pump.fun: the base rate for the market-cap band (how often coins like this one paid), what the buyers have been (winner, net loser, bot, supply seller, new), the deployer's record with how similar launches went, and an honest replay of a pick list with fees and fills. Every pump.fun trade, ever. Read-only; free to start under /free/ (300 calls a day), then paid per call in USDC over x402, from $0.005; yesterday's base rates free."
version: 1.2.1
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

You can read pumpdata.fun, a warehouse of every pump.fun trade ever, bonding curve and PumpSwap, since pump.fun's first day,
read from the chain's own ledger with the dead coins kept. `rug-check` reads a coin's contract;
`survivor-check` says whether it has lasted; this says whether coins like it have ever paid, what its buyers
have been, what its deployer has done, and what a list of picks would really have made. Every call is a read, paid
per call in USDC over x402 with your own wallet, from half a cent. Nothing here signs a trade.

## Free, before any wallet

- `GET https://pumpdata.fun/public/baserate.json`: yesterday's base rate for every market-cap band, refreshed
  hourly, the same answer the paid call gives for that day. Read this first; pay only for another window.
- `GET https://pumpdata.fun/stats.json` (or the MCP tool `stats`): yesterday on pump.fun. Launches, graduations,
  volume, traders; the top coins by peak market cap and by volume; the deployers whose coins did best, with their
  record; the fastest graduations; launches and the 1 h graduation rate per UTC hour. Never quote a number listed in
  `checks`. `summary` is a paragraph to
  quote; each wallet and coin names the paid call that goes deeper. A past day: `/stats/{YYYY-MM-DD}.json`.
- `GET https://pumpdata.fun/check/{mint}.json`: the pre-buy check in one call: `answer` (the findings as sentences), `flags`
  (serial_launcher, deployer_sells_fast, never_ran, curve_bought_at_launch, early_concentration (named bundled before Oct 28, 2026), one_wallet_bought, insiders, sold_together, lookalikes_die,
  each with a sentence), `rules_say` and the launch record behind them. Start here for any coin.
- `GET https://pumpdata.fun/launches/since.json?t=<unix seconds>` (no `t`: the last ten minutes): every launch after a moment in the last 24 hours,
  oldest first, each with its deployer's record before it (launches, graduations, gap since the last) and the
  first-10-second bundle; launches newer than the hourly fill come within the minute (`source: "live"`, bundle not yet
  read). Poll it with `t = next_since` and keep each mint once; then call `/launch` or `/deployer` only for the coins
  you are considering. `min_launches=20` keeps the serial deployers' launches; `deployer=<wallet>` one deployer's. A whole
  UTC day (today and the two before): `GET /launches/{YYYY-MM-DD}.json`.
- `GET https://pumpdata.fun/graduations/{YYYY-MM-DD}.json` (today and the two UTC days before): every coin whose bonding
  curve completed that day, with `graduated_after_s` (seconds from its create), `same_second` (the whole curve bought
  within a second of launch, before anyone could see the coin: about a third of graduations), the deployer's launches
  and graduations before it, and the day's top graduating deployers.
- `GET https://pumpdata.fun/graduations/since.json?since=<unix seconds>` (or the MCP tool `graduations`): every coin
  whose curve completed in the last hour, as it lands, with `graduated_after_s` and `same_second`; poll with `next_since`.
- `GET https://pumpdata.fun/trades/large.json?since=&min_usd=2500&side=&wallet=` (or the MCP tool `whale_trades`): every
  pump.fun buy and sell of $2,500 or more (from $1,000) in the last hour, with the wallet, the coin, SOL, USD and the market
  cap at the trade; `wallet=` for one wallet's. A record of what wallets did, not a signal. The page: /whales.
- `GET https://pumpdata.fun/public/baserate.json` (or the MCP tool `odds_by_market_cap`): yesterday's odds for every
  market-cap band, how many coins crossed it and what share did 2x, 5x, 10x, 20x within three hours. Pages: /pump-fun-odds.
- `GET https://pumpdata.fun/coin?q=<ticker or name>`: which coins a ticker means, newest first, each with its deployer.
- `GET https://pumpdata.fun/ticker/{symbol}.json` (or the MCP tool `ticker_crowd`): the crowd a new coin stands in.
  The ticker's launches over the last three UTC days (each day's first, and the ones that graduated with how long after
  the first they launched), how many launched in the last two hours, its launches and deployers over 14 days, and every
  coin with the ticker that ever graduated (the first and the biggest named). Most launches reuse a ticker (88.3% of
  October 2026's): read this before calling a coin "the" $TICKER.
- `GET https://pumpdata.fun/trending.json?window=6h&lane=new|hot|both&limit=10` (or the MCP tool `trending`): the coins
  with the most SOL flowing in (buys minus sells) over the trailing 1h, 6h or 12h, among coins without early
  concentration, dust trades, a thin pool, a one-block supply sale or a launch-slot buyout. Lanes: `new` (launched inside
  the window, curve not finished) and `hot` (any age). `buyers_in_window` counts wallets that bought, not holders. The
  answer carries its rule and its backtest (Nov 1-2 2026: 22.2% of the 6h new list graduated within a day; most listed
  coins were below their listed market cap an hour later). Not a recommendation; refreshed every 30 s.
- The record calls without paying: `GET /free/launch/{mint}`, `GET /free/deployer/{address}`, `GET /free/similar/{mint}`,
  `POST /free/wallets`, `GET /free/baserate`: the same answers, 30 calls every five minutes and 300 a day per address.
  A free key (`https://pumpdata.fun/keys`, the `x-api-key` header on the paid paths) has no daily cap.
- `GET https://pumpdata.fun/wallets/top?followable=1`: the wallet leaderboard. Wallets that win over their whole
  pump.fun record and still trade, best first, each with `why` and its recent pace; `followable=1` keeps the ones a
  copier can keep up with (under 20 trades a day, a median hold of 2 minutes or more). Not pump.fun's own
  leaderboard, which ranks recent profit.
- `https://pumpdata.fun/wallet/{address}` (a page) and `GET /free/deployer/{address}` (the same as JSON): a
  deployer's whole record and its last 90 days beside launches like its next one; the serial deployers are
  listed at `https://pumpdata.fun/deployers`, by launches and by graduation rate, never by profit.
- `GET https://pumpdata.fun/status.json`: how fresh each layer is right now (the API, the live recorder, the hourly
  fill, the base-rate crossings, the deep tables, the daily stats and wire), each `ok`, `late` or `down` with its
  `as_of`. Check it when an answer looks stale or a call fails; every answer also carries `X-Data-As-Of` and
  `X-Live-As-Of`. How each field is made, and why the launch records have no lookahead: https://pumpdata.fun/methodology.
- `GET https://pumpdata.fun/llms.txt` (what is in the warehouse), `GET https://pumpdata.fun/openapi.json` (the
  contract, with the price of each call in `x-payment-info`).
- Telegram: `/baserate 15k-28k` to @pumpdatafun_bot.

## When to use it

| you are about to | call | price |
|---|---|---|
| post an **alpha report** on a coin at $X market cap | `GET /baserate` for that band and window: "4.5% of coins at $15–28K reached 10x within 3 h this week" is the sentence that keeps the report honest | $0.005 (yesterday: free) |
| **buy** into a coin with N buyers | `POST /wallets` with the buyers' addresses: what they have been (winners, bots, supply sellers, fresh wallets) | $0.01 |
| **copy** a wallet | `GET /wallets/top?followable=1` for whole-record winners at a pace you can follow; a coin's `top_traders` on the paid `/launch` for who made money on it, each with its class | free / $0.005 |
| trust a **deployer** or a fresh launch | `GET /launch/{mint}`: launches, graduations, the best run, the bundle, the insiders' share, and how launches that looked like this one at this age went over their next day | $0.005 |
| trust a **backtest**, yours included | `POST /replay`: the picks against the chain's history with fees, fills and the dead coins | $2 a run |

## The calls

Contract: https://pumpdata.fun/openapi.json. Docs: https://pumpdata.fun/llms.txt. Worked examples in curl, node and
python: https://github.com/pumpdatafun/pumpdata-examples.

| call | asks | answers |
|---|---|---|
| `GET https://pumpdata.fun/baserate?band=15k-28k&from=<iso>&to=<iso>&venue=any` | a market-cap band (edges snap to 5k, 10k, 15k, 20k, 28k, 40k, 60k, 100k, 250k, 1000k), a window of up to 31 days, `venue` any, curve or pool | `crossed` (coins with a crossing in the window, see Definitions), `reached` {2x, 5x, 10x, 20x} as shares within 3 h, `median_peak`, the window used |
| `POST https://pumpdata.fun/wallets` `{"addresses": [...], "mint": "<optional>"}` | up to 50 wallets, optionally the coin they are buying | per wallet: `class` (winner, bot, supply_seller, net_loser, new, none) and `why` (the rule it met, with its numbers; `none` is usually a wallet too young for the rules), `pnl_sol`, `put_in`, `took_out`, `coins`, `first_seen`, `recent` (its pace). The labels are rules, not opinions |
| `GET https://pumpdata.fun/deployer/{address}` | a deployer's wallet | its launches, graduations, best run and last launch; over the last 90 days how many of its launches doubled, did 10x, held at 2x a day later or died, its newest launches by mint; and the base rate for its next launch from deployers with the same record. No coin needed |
| `GET https://pumpdata.fun/similar/{mint}` | a mint; `?limit=1..25` | the launches most like this one at the same age, named with their mints: the same deployer's prior launches first, then the nearest of the last 90 days by the deployer's record, the first-10 s buyers, the insiders' share and curve progress; for each, how it went over its next 24 h (peak, close, dead or graduated) and why it is similar. Open any of them to check |
| `GET https://pumpdata.fun/launch/{mint}` | a mint | the deployer's record (launches, graduations, best run, gaps between launches), the bundle at creation, the insiders' share of supply, `curve_bought_at_launch` (one or two wallets bought the whole curve as it launched, a quarter of graduates since Jul 2026, with the share they still hold), curve progress, the market cap now and `sol_reserve_now` (the real SOL behind it), and how launches that looked the same at this age went over the next 24 h. Paid: also its holder count, its 20 biggest wallets now (`top_holders`) and, for a coin launched since the tables' build, the 20 that made the most SOL on it (`top_traders`, each with its class) |
| `POST https://pumpdata.fun/replay` `{"picks": [{"mint", "at", "size_sol"}, ...]}` | up to 500 picks, graduates only | `202` with a job id; poll `GET /replay/{id}` (free) until `state` is `done` (or `failed`): what the picks made pick by pick and in sum, filled at the PumpSwap pool as it stood 3 s after the mark, pump.fun's fee by tier, a fixed 145,000 lamports to land each side (entry and exit), graduates that died in the sum; a pick still on the bonding curve, or outside the archive, fills nothing and is counted in `skipped_not_covered` |

Definitions: a *crossing* is a coin's first trade with a market cap inside the band (a coin that jumps over the
band in one trade has none); the *peak* is the highest market cap, curve or pool, in the 3 h after; a window ending
under 3 h before the data's as-of (`X-Data-As-Of`) is cut there; USD is at the SOL price of the trade's hour. Every answer carries `X-Data-From`
(where the data begins) and `X-Data-As-Of` (the build it comes from).

## How to pay

x402 v2, USDC on Solana. A call without payment returns **402** with the offer (price, payee, network) in the body
and the `PAYMENT-REQUIRED` header. Sign the transfer with your wallet and retry with `PAYMENT-SIGNATURE`; the
answer comes back with the receipt in `PAYMENT-RESPONSE`. Your x402 tool does the retry for you. No key, no account.

**MCP:** the same calls as tools at `POST https://pumpdata.fun/mcp` (Streamable HTTP, JSON-RPC 2.0):
`stats`, `find_coin`, `check_coin`, `top_wallets`, `launches_since`, `ticker_crowd`, `trending`, `whale_trades`, `graduations`, `odds_by_market_cap` (free), and `base_rate`, `wallet_records`, `launch_record`,
`deployer_record`, `similar_launches`, `replay`, `replay_result`. A paid tool called without `payment` or an `x-api-key` returns
the offer; call again with the `PAYMENT-SIGNATURE` value as `payment`.

**From a ClawPump agent** (the `clawpump` MCP, with the `x402` skill enabled): `x402_pay_check` on the call's URL
(free: the 402 offer, price and input schema), quote the price to the user, then `x402_pay` with `confirm_payment: true`
and `max_amount_usd` at the user's approved cap: `0.01` covers `/baserate`, `/launch` and `/wallets`, `2` covers
`/replay`. Check funds with `get_wallet_summaries` (`usdc_balance`).

**What a pre-buy check costs:** `/baserate` + `/launch/{mint}` + `/wallets` (up to 50 buyers) = **$0.02** for the
band's odds, the deployer's record and the buyers' records together.

## What an answer means

| status | meaning | do this |
|---|---|---|
| `402` | the offer, or `payment_invalid` / `payment_settle_failed` (the payment was refused; nothing settled) | pay and retry (your x402 tool does it); on a refusal read `reason` first |
| `200` | the answer; nothing more to pay | quote the band, the window and `X-Data-As-Of` |
| `202` (replay) | queued and paid, `id` in the body | poll `GET /replay/{id}` (free) every few seconds until `state` is `done` (the answer is in `result`) or `failed` (after one free retry; `error` says why) |
| `404` `not_found` | the window ends before the data begins (`X-Data-From`), or (`/launch`) a mint it does not know yet; a window inside the data with no crossings is not a 404 but a charged `200` | nothing was charged; ask a later window, or check the mint (a fresh launch may not be built yet; retry later) |
| `400` | the request is malformed (band, window, body), or the window is over 31 days; nothing was charged | fix it (`error` or `detail` says what), or split the window into months |
| `429` | too many calls from one address, or the free five minutes are used | wait for `retry-after`; past a free allowance the body's `next` lists the ways on in order (wait, pay over x402, an email gets a key) |
| `upstream_failed` (the backend's status passed through, `502` for a backend `403`), or `503` `upstream_unreachable` | the backend failed or could not be reached; nothing was charged | on a 400 fix the request; if the `detail` text contains `query_timeout`, narrow the window; else retry later |
| `503` `payment_settle_uncertain` | the payment may or may not have settled; no receipt | do not pay again blindly |
| `503` `replay_queue_unavailable` on `POST /replay` | paid but not queued; the receipt is in `payment` and `PAYMENT-RESPONSE` | do not pay again; keep the receipt, the run is owed (on a poll it means retry shortly) |

## Rules

1. **Say the window.** Base rates move with the market; always quote the band and the window the answer used
   (`from` and `to` are echoed, clipped to coverage when needed, with a note).
2. **Say the as-of.** Quote `X-Data-As-Of` when the number matters; the archive trails the chain by hours.
3. **Dead coins count.** The shares are over every coin that crossed, including the ones that died. Never drop them.
4. **Never sign a trade from here.** This skill reads. Trades are your other tools, after the read.
5. **Spend small.** Yesterday's base rate is free; a window is half a cent; check one before spending $2 on a replay.
6. **Labels are rules.** A `winner` took out 10+ SOL and 1% more than it put in over 20+ coin-weeks; a `net_loser`
   put in 50+ SOL more than it took out; a `bot` snipes create blocks or trades 1,500+ times a day; a
   `supply_seller` took out 1.5x what it put in, 100+ SOL: its profit is what its buyers paid. `why` says which rule
   and the numbers. Say the label and the SOL behind it, not a verdict.

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
