# pumpdata: the base rate before the call

You can read pumpdata.fun, a warehouse of every PumpSwap trade ever and every pump.fun bonding-curve trade since
March 2025, read from the chain's own ledger with the dead coins kept. `rug-check` says whether a coin is safe to
touch; this says whether coins like it have ever paid. Every call is a read, paid per call in USDC over x402 with
your own wallet. Nothing here signs a trade.

## When to use it

- Before an **alpha report** on a coin at $X market cap: get the base rate for that band first. "4.5% of coins at
  $15–28K reached 10x within 3 h this week" is the sentence that keeps the report honest.
- Before a **buy** into a coin with N buyers: send the buyers' addresses and read what they have been (winners, bots,
  supply sellers, fresh wallets).
- Before trusting a **deployer**: how many launches, how many graduated, the best run, and how launches that looked
  like this one at this age went over their next day.
- Before trusting a **backtest**, yours included: replay the picks against the chain's history with fees and fills.

## The calls

Contract: https://pumpdata.fun/openapi.json. Docs: https://pumpdata.fun/llms.txt.

| call | asks | answers | price |
|---|---|---|---|
| `GET https://pumpdata.fun/baserate?band=15k-28k&from=<iso>&to=<iso>&venue=any` | a market-cap band (edges snap to 5k, 10k, 15k, 20k, 28k, 40k, 60k, 100k, 250k, 1000k) and a window | how many coins first traded inside the band, the share that reached 2x, 5x, 10x, 20x within 3 h, the median peak | $0.005 |
| `POST https://pumpdata.fun/wallets` `{"addresses": [...], "mint": "<optional>"}` | up to 50 wallets, optionally the coin they are buying | per wallet: class (winner, bot, supply_seller, new, none), pnl_sol, put_in, took_out, coins, first_seen | $0.01 |
| `GET https://pumpdata.fun/launch/{mint}` | a mint | the deployer's record, the bundle at creation, the insiders' share of supply, curve progress, and how launches that looked the same at this age went over the next 24 h | $0.005 |
| `POST https://pumpdata.fun/replay` `{"picks": [{"mint", "at", "size_sol"}, ...]}` | up to 500 picks | a queued run (202 with an id; poll `GET /replay/{id}`): what the picks made, pick by pick and in sum, fees and fills included, dead coins counted | $2 |

Definitions: a *crossing* is a coin's first trade with a market cap inside the band (a coin that jumps over the
band in one trade has none); the *peak* is the highest market cap, curve or pool, in the 3 h after; a window ending
under 3 h ago is cut at 3 h ago; USD is at the SOL price of the trade's hour. Every answer carries `X-Data-From`
(where the data begins) and `X-Data-As-Of` (the build it comes from). A window with no data answers 404 and costs
nothing.

## How to pay

x402 v2, USDC on Solana. A call without payment returns **402** with the offer (price, payee, network) in the body
and the `PAYMENT-REQUIRED` header. Sign the transfer with your wallet and retry with `PAYMENT-SIGNATURE`; the
answer comes back with the receipt in `PAYMENT-RESPONSE`. Your x402 tool does the retry for you.

**MCP:** the same calls as tools at `POST https://pumpdata.fun/mcp` (Streamable HTTP, JSON-RPC 2.0). `tools/list`
shows the calls that answer; a tool called without `payment` returns the offer; call again with the
`PAYMENT-SIGNATURE` value as `payment`.

## Rules

1. **Say the window.** Base rates move with the market; always quote the band and the window the answer used
   (`from` and `to` are echoed, clipped to coverage when needed, with a note).
2. **Say the as-of.** Quote `X-Data-As-Of` when the number matters; the archive trails the chain by hours.
3. **Dead coins count.** The shares are over every coin that crossed, including the ones that died. Never drop them.
4. **Never sign a trade from here.** This skill reads. Trades are your other tools, after the read.
5. **Spend small.** A base rate is half a cent; check one before spending $2 on a replay.

## Output shape (base rate)

```
BASE RATE · $15–28K · 2026-10-15 00:00Z → 2026-10-16 00:00Z · as of 2026-10-16T01:33Z
crossed 1,029 · 2x 31.4% · 5x 10.5% · 10x 4.5% · 20x 1.5% · median peak 1.43x
```
