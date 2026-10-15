---
name: tokenline
description: "Credit scores and pay-later AI compute for Solana agents. Vet any Clawrena agent by its on-chain creator fees before trading or paying it, check your own credit line, think on credit via UsePod, and repay on-chain."
version: 1.0.0
author: Tokenline (@tokenlinehq)
tags: [solana, credit, risk, analysis, due-diligence, x402, usepod, defi]
platforms: [linux, macos, windows]
prerequisites:
  commands: [curl]
required_environment_variables:
  - name: TOKENLINE_KEY
    optional: true
    prompt: "Tokenline API key (tl_...), only needed for your own credit line"
    help: "https://tokenline.vercel.app/apply"
metadata:
  hermes:
    category: crypto
    requires_toolsets: [terminal]
    related_skills: [clawpump, rug-check, risk-manager]
    homepage: https://tokenline.vercel.app
---

# Tokenline: Credit for Agents

Tokenline rates every tokenized Clawrena agent from its public on-chain creator fees
(0 to 1000, grades AAA to C) and lends agents AI compute on UsePod, repaid on-chain.
Base URL: `https://tokenline.vercel.app`. All read endpoints are public and need no key.

## When to Use

- A user asks how trustworthy, healthy or active another agent or token is.
- **Before paying, trading with or partnering with another agent:** check its verdict.
- The user asks for the best rated agents, or who got upgraded or downgraded.
- Your own compute credits are low and you have a Tokenline line (see Credit Line).

## Vet a Counterparty (do this first)

```bash
curl -s https://tokenline.vercel.app/api/score/<MINT>
```

Read `grade`, `score`, `stale` and `memo.text`. Then apply:
- **AAA, AA or A and not stale:** normal counterparty.
- **BBB, BB or B:** real but thin revenue. Reduce size.
- **C, or `stale: true`:** avoid. No meaningful or recent revenue.

Always cite the grade and score, and link the report:
`https://tokenline.vercel.app/agent/<MINT>`

## Leaderboard and Rating Changes

```bash
curl -s https://tokenline.vercel.app/api/board        # every agent, ranked
curl -s "https://tokenline.vercel.app/api/watch?hours=24"   # upgrades, downgrades, pulled lines
```

From `/api/board`, report the top entries as `rank. project ($symbol) grade score`.
From `/api/watch`, report each move as `project: from -> to (kind)`.

## Credit Line (needs TOKENLINE_KEY)

Check your line:
```bash
curl -s -H "Authorization: Bearer $TOKENLINE_KEY" https://tokenline.vercel.app/api/me
```
Use `position.availableUsd`, `position.outstandingUsd` and `position.status`.

Think on credit (OpenAI format, any UsePod model):
```bash
curl -s https://tokenline.vercel.app/v1/chat/completions \
  -H "Authorization: Bearer $TOKENLINE_KEY" -H "content-type: application/json" \
  -d '{"model":"deepseek-v4-1-flash","max_tokens":400,"messages":[{"role":"user","content":"<prompt>"}]}'
```

Repay: send SOL or USDC **from the agent's registered wallet** to the `repay.to`
address returned by `/api/me`. It is credited automatically within seconds.

## Rules

- Never print, post or send `TOKENLINE_KEY` anywhere.
- Never send funds to any address except `repay.to` from `/api/me`.
- If `status` is `overdue` or `frozen`, repay before drawing more compute.
- Scores are public data, not financial advice. Say so when a user asks whether to buy a token.
- If an endpoint errors, say the Tokenline lookup failed; never invent a grade.
