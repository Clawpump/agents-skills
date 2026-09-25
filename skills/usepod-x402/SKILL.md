---
name: usepod-x402
description: "Buy LLM inference per request from UsePod over x402 on Solana: read the 402 quote, pay USDC, retry byte-identically, and spend leftover credit with a signed proof. Includes a live-probed error catalogue."
version: 1.0.0
author: Jagadeeshftw
tags: [x402, usepod, inference, solana, usdc, payments, agent-payments, clawpump]
platforms: [linux, macos, windows]
prerequisites:
  commands: [curl, python3]
required_environment_variables:
  - name: USEPOD_BASE_URL
    optional: true
    prompt: "UsePod base URL (default https://api.usepod.ai)"
    help: "Override only for a local mock gateway."
metadata:
  hermes:
    category: crypto
    requires_toolsets: [terminal]
    related_skills: [clawpump, laso-finance]
    homepage: https://usepod.ai
---

# usepod-x402 — Pay-per-request inference on Solana

Buy inference one request at a time from UsePod. No account, no API key, no
subscription: an unpaid request returns `402` with a price, you pay USDC on
Solana, and you retry. The agent's own wallet is the credential.

Use it when you need a model call that is **metered and receipted** — each call
has a quote id, an amount and a transaction signature you can show later — or
when you have no API key for a model you want.

Endpoint: `POST {USEPOD_BASE_URL}/proxy/x402/v1/chat/completions`
(default base `https://api.usepod.ai`). OpenAI-shaped request body.

## The flow

1. **Send the request unpaid.** You get `402` with a `PAYMENT-REQUIRED` header:
   base64 JSON. Decode it.
2. **Read a rail out of `accepts[]`.** Each entry carries `quote_id`,
   `scheme`, `network`, `pay_to`, `asset`, `amount_microunits`, `expires_at`
   and `body_hash`.
3. **Pay `amount_microunits` of USDC to `pay_to`** on the quoted network. Use
   the ClawPump MCP wallet tools, or whatever signer the agent already has.
   **This skill never handles a private key.**
4. **Retry the byte-identical request** with a `PAYMENT-SIGNATURE` header
   carrying the quote id and your transaction signature.

`body_hash` is `sha256("POST\n<path>\n<body>")`. The quote is bound to the
exact bytes you sent. Re-serialising the JSON between the 402 and the retry —
different key order, different spacing — changes the hash and the retry is
refused. Keep the raw body string and send it again unchanged.

## The quote is a cap, not a price

`mode` is `cap-with-surplus-credit`. You are charged for what the call
actually consumes; the unused remainder of the cap becomes **surplus credit
attached to your payer wallet**.

The practical consequence: price the cap on `max_tokens`, and a short answer
leaves the remainder as credit. That credit pays for later calls with **no
on-chain transaction and no network fee at all**, which is the cheapest way to
run a stream of small calls.

**Do not try to buy credit by overpaying.** Sending more USDC than
`amount_microunits` does not top up your balance — measured live, $0.04 paid
above two 5-micro caps produced no spendable credit and was not refunded. Only
the unused part of a cap you were actually quoted becomes credit. Pay the cap,
never more.

Credit accrues in **micro-units**, so it builds slowly: a call quoted at 9 that
consumes 6 leaves 3. Expect to pay on-chain until a deliberately large cap has
left a real remainder.

## Spending surplus credit

Retry with `scheme: "balance"` instead of paying again. Sign the ASCII string

```
usepod-x402-spend:<quote_id>
```

with the payer wallet (ed25519, 64 bytes) and send the envelope:

```json
{ "quote_id": "…", "network": "solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp",
  "asset": "USDC", "payer_wallet": "<pubkey>", "scheme": "balance",
  "proof": "<signature>" }
```

**`proof` is top-level.** The gateway's own error text says `payload.proof`,
but a nested `payload` object is ignored — verified against the live gateway.
If a balance spend keeps failing with a proof error while your signature is
correct, this is why.

If credit is short you get `balance_insufficient` and **nothing is spent** —
fall back to paying on-chain. Treat that error as routine, not as a failure.

## Hard rules

- **`max_tokens` (or `max_completion_tokens`) is required.** Omit it and the
  request is rejected before any quote is issued.
- **Streaming is not supported** on the x402 path. `stream: true` is refused.
- **Retry byte-identically.** See `body_hash` above.
- **Quotes expire.** Check `expires_at` before paying; if it has passed, start
  again from step 1 rather than paying against a dead quote.
- **Never put a private key in a skill, a prompt or a log.** Delegate signing.

## Errors, and what to do

Full table with provenance in `references/x402-errors.md`.

| Error | Status | Do this |
|---|---|---|
| `missing_max_tokens` | 400 | Add `max_tokens`; you were never quoted. |
| `stream_not_supported` | 400 | Drop `stream`; use a normal completion. |
| `quote_mismatch` | 400 | Your retry body differs from the quoted bytes. |
| `unknown_quote` / `quote_expired` | 400 | Re-request and get a fresh quote. |
| `tx_not_found` | 400 | Payment not confirmed yet — wait, then retry. |
| `balance_insufficient` | 400 | No credit. Pay on-chain. Nothing was spent. |
| `balance_proof_invalid` | 400 | Signature does not verify for `payer_wallet`. |
| `no_provider` | 503 | Model has no healthy provider; pick another. |

## Routing headers

`X-Pod-Routing-Mode` (`marketplace-only` / `centralized-only`),
`X-Pod-Providers`, `X-Pod-Max-Price-Input` and `X-Pod-Max-Price-Output` go on
the **initial** request, not the retry.

Measured live: they do **not** change the quote. An unrouted request, both
routing modes, an unknown provider name and an unpayably low price floor all
returned the same cap for the same model, and no `x-pod-*` headers come back on
the 402. Treat routing as a preference that the settled response reports rather
than a lever on price — the paid response carries `x-pod-route` and
`x-pod-provider-id`, which is how you learn who actually served you.

## Cost discipline

Per-request payment makes overspending easy and quiet. Before wiring this into
anything autonomous:

- Set a **lifetime ceiling** and refuse past it, in the component that signs —
  not only in the component that decides. A ceiling enforced in one place is a
  ceiling with one bug between you and an empty wallet.
- Set a **per-call maximum** and refuse any quote above it, so a mispriced or
  hostile quote cannot drain the wallet in a single call.
- **Count the network fee**, not just the quote. On a small quote the Solana
  fee can exceed the inference cost.
- **Reserve before you pay and settle after**, so a crash mid-payment cannot
  lose the record of money that left.
- **Keep the receipt** — quote id, amount, signature, and what the call was
  for. Per-request billing is only auditable if you write it down.

## Checking a quote without paying

`scripts/usepod_x402.py quote --model gpt-4o-mini --prompt "hello"` prints the
decoded quote, the cap in micro-USD and the computed `body_hash`, and pays
nothing. Use it to see a price before committing, and to confirm your body
hashing matches the gateway's before you debug a `quote_mismatch`.
