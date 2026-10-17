# AnsemHub

AnsemHub reads Ansem.io's public on-chain activity on Solana (Z500 boost
purchases, $ANSEM burns, launches) and serves it as typed JSON. It is
**independent of Ansem.io** (not affiliated, not endorsed), **read-only**,
and needs **no API key**. AnsemHub never builds a Buy, never holds a key,
and never signs anything. Trading happens only through the wallet tools
the host agent already has (ClawPump `mcp_clawpump_*`).

Disclaimer, repeat it to the user whenever money is involved: *AnsemHub is
not financial advice. Boosts are paid promotion, not a quality signal. A
burn is permanent. The backtest of the boost signal showed no edge; trade
it only if you have decided to.*

- REST base: `https://api.ansemhub.com`
- MCP (streamable HTTP, stateless, no auth): `https://api.ansemhub.com/mcp`
- Site: `https://ansemhub.com` - agent page `https://ansemhub.com/agent`

Add the MCP to Hermes (`~/.hermes/config.yaml`):

```yaml
mcp_servers:
  ansemhub:
    url: https://api.ansemhub.com/mcp
```

Tools then surface as `mcp_ansemhub_<tool>`: `get_boosts`, `get_coin`,
`get_burn_score`, `get_leaderboard`, `get_agent_signals`. Each returns the
same JSON as the REST route below. Without the MCP, `curl` the REST routes.

## Endpoints (all GET, public, no auth)

Rate limits per IP: `/api/burn-score/*` and `/api/agent/*` 180/min;
everything else the general bucket, 10 rps with a burst of 30.

Full field lists: [references/api.md](references/api.md). Every address is
base58 and printed whole; every amount is an exact integer in base units
(`lamports` = SOL x 1e9, `_raw` = $ANSEM x 1e6) unless the field says
`_sol` / `_usd`.

| Route | What | Params |
|---|---|---|
| `/api/boosts` | Latest Z500 boosts, newest first | `limit` 1-100 (default 50), `before` sig, `after` sig |
| `/api/coins` | Boosted-coin index | `limit` 1-100, `offset`, `q`, `sort` = `last_boost` / `boosts_24h` / `launched` |
| `/api/coins/{mint}` | One coin: identity, launch, boosts, snapshot, airdrop | - |
| `/api/burn-score/{wallet}` | Ansem-credited $ANSEM burned, tier, rank | - |
| `/api/burn-score/{wallet}/burns` | That wallet's burns (last 50) | - |
| `/api/burn-score/leaderboard` | Top 100 burners | - |
| `/api/market/tickers` | SOL + $ANSEM price | - |
| `/api/agent/signals` | AnsemHub agent buy/sell signals, due now | `since_id` int |
| `/api/agent` | Agent page read: wallets, balance, kill switch, fills | - |

### `/api/boosts` sample (one item)

```json
{"items":[{"sig":"<boost tx signature, 88 chars base58>",
  "slot":361234567,"ts":1755860000,
  "coin_mint":"8mQrT2vKzY4pW9nH3xLd6RtBcQeF1uS7aJmN5gVkpump",
  "coin":{"mint":"8mQrT2vKzY4pW9nH3xLd6RtBcQeF1uS7aJmN5gVkpump","ticker":"Z-14","name":"z-14","image_url":null},
  "coin_confidence":"derived","copurchase":null,
  "tier":"500x","amount_lamports":52551300000,"amount_sol":52.5513,"amount_usd":3999.0,
  "payer":"5HfKFiDyXdULcJDZFCD8zyR6UhB1Fpz3ZFfX7vTwLY1Q","is_creator":false,
  "snapshot":{"symbol":"Z-14","price_usd":0.0024,"mcap_usd":2400000,"liq_usd":180000,"age_s":61200,"curve":0.61},
  "buyer_intel":null,"enriched":true,"dropped":false}],
 "next_before":"<sig of the last item>"}
```

`coin_mint` is `null` on roughly 40% of boosts: the payment names no coin
on-chain. That is a fact, not a bug. `copurchase` (what the BUYER bought
near the boost) is an observation about the buyer, never the boosted coin.

### `/api/burn-score/{wallet}` sample

```json
{"wallet":"5HfKFiDyXdULcJDZFCD8zyR6UhB1Fpz3ZFfX7vTwLY1Q","ansem_burned_raw":"370508000000",
 "tier":"diamond","first_burn_at":1755000000,"burn_count":3,"computed_at":1755860000,"partial":false,
 "rank":12,"population":85,"percentile":"14.1","last_burn_at":1755800000,
 "next_tier":"diamond_plus","next_tier_raw":1000000000000}
```

`ansem_burned_raw` is base units: divide by 1e6 for $ANSEM. Tiers: Gold
92,627 / Diamond 370,508 $ANSEM (live-read from ansem.io config).

### `/api/burn-score/leaderboard` sample

```json
{"rows":[{"rank":1,"wallet":"5HfKFiDyXdULcJDZFCD8zyR6UhB1Fpz3ZFfX7vTwLY1Q","score_raw":1200000000000,
  "tier":"diamond_plus","burn_count":9,"last_burn_at":1755800000}],
 "population":85,"computed_at":1755860000,"thresholds_read_at":"2026-08-19T10:00:00Z"}
```

### `/api/coins/{mint}` sample (trimmed)

```json
{"mint":"8mQrT2vKzY4pW9nH3xLd6RtBcQeF1uS7aJmN5gVkpump",
 "coin":{"mint":"8mQrT2vKzY4pW9nH3xLd6RtBcQeF1uS7aJmN5gVkpump","ticker":"Z-14","name":"z-14","image_url":null},
 "launch":{"mint":"8mQrT2vKzY4pW9nH3xLd6RtBcQeF1uS7aJmN5gVkpump","sig":"<launch tx signature>","ts":1755798800,
  "creator":"5HfKFiDyXdULcJDZFCD8zyR6UhB1Fpz3ZFfX7vTwLY1Q","tier":"gold","airdrop_live":false},
 "boosts":[],"snapshot":null,"snapshot_fetched_at":null,"airdrop":null}
```

### `/api/agent/signals?since_id=0` sample

```json
[{"id":41,"kind":"buy","mint":"8mQrT2vKzY4pW9nH3xLd6RtBcQeF1uS7aJmN5gVkpump",
  "sol_lamports":50000000,"boost_sig":"<boost tx signature, 88 chars base58>",
  "due_at":1755860000,"stale":false},
 {"id":42,"kind":"sell","mint":"8mQrT2vKzY4pW9nH3xLd6RtBcQeF1uS7aJmN5gVkpump",
  "sol_lamports":null,"boost_sig":"<boost tx signature, 88 chars base58>",
  "due_at":1755860300,"stale":false}]
```

Wire shape: `{id, kind: "buy" | "sell", mint, sol_lamports, boost_sig,
due_at, stale}`. Rows are returned only once `due_at <= now`, `id >
since_id`, ascending, at most 50 per call. `sol_lamports` is set on `buy`
only. `stale` is `true` on a buy whose `due_at` is more than 90 s old.
All judgement (entry rule, size 0.05 SOL, exit +5 min, kill switch at
0.5 SOL, 1 buy per mint per hour, max 10 open) lives on the server; the
agent never decides size or timing.

## Agent recipe (the AnsemHub trader loop)

Run this as a cron job every 30 s (`/cron add "every 30s" "..."` with this
skill attached). Keep `since_id` in the job's continuity output; start at
`0` the first time.

```
every 30 s:
  rows = get_agent_signals(since_id)        # MCP, or GET /api/agent/signals?since_id=<since_id>
  for row in rows (ascending id):
    if row.kind == "buy":
      if row.stale: skip                    # too late; the window is gone
      q = mcp_clawpump_swap_quote(input = SOL, output = row.mint, amount = row.sol_lamports)
      mcp_clawpump_swap_execute(q)          # exactly row.sol_lamports, never more
    if row.kind == "sell":
      bal = agent wallet token balance of row.mint
      if bal > 0: swap_execute(row.mint -> SOL, amount = bal)   # the FULL balance
  since_id = id of the last row seen
```

Rules, none of them tunable:

1. **Never buy off-signal.** No row, no buy. Do not buy from `/api/boosts`
   directly, do not buy a coin the user mentions, do not re-buy a stale row.
2. **Never exceed `sol_lamports`.** Quote and execute with exactly that
   amount. If the quote cannot fill it, skip the row.
3. **Sell the full balance** of `mint` on a sell row. A sell is safe late:
   execute it even if `due_at` is old. If the balance is 0, skip.
4. **Stop after 3 consecutive execute errors.** Do not retry the fourth.
   Tell the user what failed, with the row `id`, `mint` and the error text,
   and wait for them.
5. Report every fill to the user with the full mint and the tx signature,
   printed whole. Never shorten an address.

`https://ansemhub.com/agent` shows the same trades read back from chain,
with the fee wallet's burns. What the page shows is the record, not what
the agent says it did.

## Install

```
hermes skills install well-known:https://ansemhub.com/.well-known/skills/ansemhub
hermes skills install https://ansemhub.com/.well-known/skills/ansemhub/SKILL.md
```

Hosted ClawPump agents: toggle `AnsemHub` in the dashboard skill list
(registry entry in `Clawpump/agents-skills`).
