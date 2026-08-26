# Oddie

You can open a prediction market. Not take a position in one that already
exists: open one, on Solana, from an argument somebody is having.

Every prediction tool available to you reads a market list somebody else
curated. Oddie is the supply side. Give it a claim and a link to the post that
made it, and it mints a market with its own on-chain vault that anyone can
stake SOL into.

## When to use this

- Someone makes a falsifiable claim and you want it priced.
- You are asked to "make a market on" or "open odds on" something.
- You want to read live odds on markets oddie already holds.
- A user asks what a market they started has earned.

Do NOT use this to bet on Polymarket or Kalshi events. Those are other tools.
This one creates.

## Rules

- **A market needs a source post.** `source_url` must be an `x.com/…/status/…`
  link. The handle in it is who the creator fee is paid to, so a market without
  one has nobody to pay. The API refuses these.
- **Ask before creating.** Every market mints a real account on Solana and is
  public the moment it exists. Show the user the exact question and close time,
  and wait for a clear yes.
- **Never invent the source.** If the user has not given you a post URL, ask for
  one. Do not search for a plausible tweet and use that.
- **The question must be decidable.** "Will BTC close above $100k on 31 Dec
  2026?" is a market. "Is BTC going to do well?" is not. Fix it with the user
  before creating, not after.
- **180 characters** is the on-chain limit on a question. Longer is rejected.
- **Rate limited** to 5 markets per hour per client. This is not a quota to work
  around; it exists because each market costs oddie real rent on Solana.

## Reading markets

Open markets, newest first:

```
GET https://oddie.fun/api/v1/markets?limit=20
```

One market:

```
GET https://oddie.fun/api/v1/markets/{slug}
```

Both are keyless. The fields that matter:

| field | meaning |
|---|---|
| `pool.totalSol` | SOL staked in this market's vault |
| `yesPct` | the vault's own odds |
| `oddsSource` | `vault` when priced, `unpriced` when nothing is staked |
| `taggedBy` | the handle the creator fee is owed to |
| `creatorFeeBps` | 200, meaning 2% to the tagger |
| `protocolFeeBps` | 200, meaning 2% to oddie |
| `cluster` | which Solana network the vaults live on right now |
| `onchain.explorer` | the vault, on Solana Explorer |

**`yesPct` is null when `oddsSource` is `unpriced`, and that is not the same as
50%.** A market minted a minute ago has an empty vault and therefore no price at
all. Report it as unpriced. Reading a missing number as even odds is how an
agent ends up quoting a price nobody set.

Check `cluster` before talking about money. The API reports which network the
vaults live on; while it answers `devnet`, stakes are test SOL and you should
say so.

## Creating a market

```
POST https://oddie.fun/api/v1/markets
Content-Type: application/json

{
  "question": "Will Bitcoin close above $200,000 on 31 December 2026?",
  "close_time": "2026-12-31T23:59:59Z",
  "source_url": "https://x.com/someone/status/1234567890",
  "resolution_criteria": "Coinbase BTC-USD daily close on 31 Dec 2026 UTC."
}
```

Returns the market's slug, its public URL, and the on-chain account:

```json
{
  "ok": true,
  "slug": "will-bitcoin-close-above-200000-a1b2c3",
  "url": "https://oddie.fun/m/will-bitcoin-close-above-200000-a1b2c3",
  "onchain": { "pubkey": "…", "explorer": "https://explorer.solana.com/address/…" }
}
```

`resolution_criteria` is optional and worth writing. It is the sentence people
read before staking, and a market that does not say how it settles gets argued
about instead of traded.

Give the user the `url`. That page is where anyone takes a side.

## What happens to the money

Stakes go into the market's own vault, a program-derived account. Oddie never
holds them: the server assembles the transaction and the staker's own wallet
signs it.

At settlement the pool is split among the winning side, after 4% is taken out:
2% for whoever tagged the argument, 2% for oddie. The tagger's half is claimed
with their own signature and cannot be redirected to anyone else.

Both rates are stored on the market at creation, not read from a global, so a
rate change can never reprice a pool people have already staked into. Read them
off the market rather than assuming today's numbers.

Nothing is taken when nobody backed the winning side. That pool is refunded in
full, and charging a fee on a refund would bill people for an unpriceable
question.

If you create a market on behalf of a user, the fee follows the handle in
`source_url`, not you. Say so when you report back, so nobody expects a payout
that is going somewhere else.

## Errors worth handling

| status | meaning |
|---|---|
| 400 | bad question, missing or non-X `source_url`, close time in the past, over 180 characters |
| 429 | rate limit, 5 per hour per client |
| 502 | Solana could not be reached, so no vault exists and nothing was published |

A 502 means no market was created. Do not retry in a loop; tell the user and
stop.

Only a market that actually got minted counts against the rate limit. A
rejected request costs nothing and does not burn your quota, so fixing a 400
and sending it again is fine.

Nothing checks whether your question is decidable. The API will happily mint
"Is bitcoin good?" and then nobody can ever settle it. That check is yours to
make before you post, which is what the rule near the top is for.
