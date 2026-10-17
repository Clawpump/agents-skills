---
name: kestiv
description: "Turns a Solana token's creator fees into a founder stake locked in uncancellable Jupiter locks. Runs a gated buy loop with a dry-run mode, a UsePod veto and hard spend limits. Never sells."
version: 0.1.0
author: Kestiv (built on Hermes)
tags: [solana, pump-fun, creator-fees, vesting, jupiter-lock, founder-stake, agent, clawpump]
platforms: [linux, macos]
prerequisites:
  commands: [node, npm]
required_environment_variables:
  - name: KESTIV_WALLET
    prompt: "Kestiv agent wallet address (public key)"
    help: "The public key of the wallet that receives creator fees and holds the buy budget"
  - name: FOUNDER_WALLET
    prompt: "Founder wallet address (public key)"
    help: "Receives the founder share of fees and is the creator of the locks"
  - name: KESTIV_MINT
    prompt: "Token mint address"
    help: "The Solana mint of the token whose founder stake Kestiv builds"
  - name: KESTIV_KEYPAIR_PATH
    prompt: "Path to the Kestiv keypair JSON (solana-keygen format, mode 600)"
    help: "Only read by real runs, never by --dry-run. Keep it outside any repo"
  - name: CLAWPUMP_API_KEY
    prompt: "ClawPump partner API key"
    help: "https://clawpump.tech"
  - name: HELIUS_API_KEY
    optional: true
    prompt: "Helius RPC key (optional, enables the holder count and a reliable RPC)"
    help: "https://dev.helius.xyz"
  - name: SOLANA_RPC_URL
    optional: true
    prompt: "Custom Solana RPC URL (optional, overrides Helius and the public endpoint)"
    help: "Use a private RPC for real runs, the public endpoint rate-limits"
  - name: USEPOD_MODEL
    optional: true
    prompt: "UsePod model for the trade-quality veto (optional, default deepseek-v4-flash)"
    help: "https://docs.usepod.ai"
metadata:
  hermes:
    category: crypto
    requires_toolsets: [terminal]
    related_skills: [clawpump, rug-check]
---

# kestiv: founder stake from creator fees

Kestiv is a CLI agent. Creator fees for one token land in the Kestiv wallet.
It forwards the founder's share, and uses the rest to buy that token and lock
it in a new Jupiter lock for the founder. Each lock is created with cancel and
change-recipient set to nobody, which cannot be changed later, so nobody can
cancel or redirect the stake and Kestiv's key cannot move it.

There is **no sell code path**. Kestiv only buys and locks.

## Setup

Kestiv runs from its own repo. Clone it once and point the wrapper at it:

```bash
git clone https://github.com/mystiquemide/kestiv.git ~/kestiv
export KESTIV_HOME=~/kestiv
```

Needs Node 22 or newer. `scripts/kestiv.sh` installs and builds the agent on first use.

Helper: `scripts/kestiv.sh` wraps the CLI. Set `KESTIV_HOME` to the Kestiv repo
checkout (`agent/dist` is built on first use).

## When to Use

- A user asks for the state of their Kestiv stake, budget or last run.
- A user wants to know why Kestiv did not buy ("what is it waiting on?").
- A user wants a safe preview of what the next run would do, on their token or any live token.
- Setting up Kestiv for a new token (`init`), or running the loop.

Do not use it for launching tokens, swapping other assets or checking token
safety. Use `clawpump` and `rug-check` for those.

## Commands

All commands run through the wrapper. From this skill directory:

```bash
scripts/kestiv.sh status
scripts/kestiv.sh run-once --dry-run
scripts/kestiv.sh run-once --dry-run --mint <MINT>
scripts/kestiv.sh init
scripts/kestiv.sh run-once
scripts/kestiv.sh loop
scripts/kestiv.sh loop --dry-run
scripts/kestiv.sh config add-fee-source <PUBKEY>
```

- `status`: config presence per variable (set or missing, never values), cluster
  and RPC kind, mint, lock count, slice counts, cooldown, last run and budget.
  Safe at any time.
- `run-once --dry-run`: evaluates every gate with its value and threshold, takes
  a real Jupiter quote and one free unpaid UsePod call, and prints what it
  would do. Every line is prefixed `DRY-RUN`. Sends nothing, pays nothing, does
  not read the keypair. `--mint <MINT>` runs it against any live token, only in dry-run.
- `init`: validates config, prints the review block, and asks the user to type
  the last 4 characters of the mint. Then it writes the write-once keys `mint`,
  `founder` and `vesting_terms`. The user must type the confirmation, do not answer it for them.
- `run-once`: one real iteration. Locks any unlocked tokens first, records new
  inflows, forwards the founder share, then applies the gates and may buy and lock.
- `loop`: repeats `run-once` with a random 30 to 90 minute pause.
- `config add-fee-source <PUBKEY>`: marks a sender as creator fees. Transfers
  from unlisted senders count as seed funding and are not split with the founder.

## Safety Rules

1. Never sell, swap out, transfer out or withdraw Kestiv's tokens by any means.
2. Never edit the vesting terms, the cap or the write-once config. Do not rerun
   `init` with different values to get around the write-once check.
3. Run `run-once --dry-run` and show the output to the user before the first
   real `run-once` or `loop` on any token, and after any config change.
4. Never print, log, paste or read back keys, keypair contents, API keys or RPC
   URLs. `status` is the only way to show configuration.
5. Real runs require explicit user confirmation each time. Never start `loop`
   without it.
6. Only add a fee source the user gave you. Do not guess ClawPump's forwarder address.
7. `--mint` is for dry-run demos only. Do not point real runs at another token.

## Reading the Output

The first line is `<STATE> <reason>`.

| State | Meaning |
|---|---|
| `WAITING` | A precondition is not met. No money moved this run. |
| `SKIPPED` | The gates passed to the quote or veto stage, then a check refused the buy. |
| `BOUGHT` | A slice was bought, then locked in the same run. |
| `CAP_REACHED` | The stake hit the cap. Unspent budget goes to the founder. |
| `WOULD_BUY` | Dry-run only: every evaluated gate passed. |
| `ERROR` | A step failed, for example a lock with changed terms. Read the error line, do not retry blindly. |

Common reasons: `cooldown`, `volume_below_min`, `volume_unavailable`,
`holders_below_min`, `holders_unavailable` (needs Helius), `not_enough_trades`,
`budget_below_min_slice`, `cap_headroom_below_min_slice`,
`price_impact_too_high`, `price_above_vwap`, `usepod_skip`,
`usepod_quote_too_high`, `usepod_unavailable`, `pending_confirmation`,
`insufficient_sol_for_lock`, `lock_terms_violation`.

Each `gate PASS|FAIL` line shows the measured value and the threshold. The
volume gate names its source: `clawpump`, `swaps_24h`, or `swaps_lower_bound`
(the fetched swaps did not cover 24 hours, so the number is a floor).

Lead with the state and reason, then the one or two gates that decided it. Give
amounts in SOL and percentages, and say plainly when a value is unavailable.

## Pitfalls

- The public Solana RPC rate-limits the swap history fetch. Suggest a private RPC before real runs.
- Jupiter's price impact for pump.fun includes the curve fee of roughly 1.25%, so small pools hit the impact limit quickly.
- A dry-run wallet balance below the ops reserve shows `budget_below_min_slice`. The quote in that case is only a probe at the minimum slice.
- `pending_confirmation` means a previous buy has not confirmed. Do nothing, the next run reconciles it.
- Not financial advice. Kestiv reduces spending risk with hard limits, it does not guarantee returns.

## Notes for Hermes

- Use the `terminal` tool. Variables flow from `~/.hermes/.env`.
- The wrapper builds `agent/dist` once if it is missing, which needs `npm` and network access.
- It complements `clawpump` and `rug-check`, it never replaces their confirmation rules.
