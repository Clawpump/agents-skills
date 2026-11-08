---
name: mapixa
description: "Read Mapixa's public Solana memecoin desk over MCP: the desk's grade (A, B, C or NO) with the written rule texts behind it, a coin card by mint with on-chain facts, the day's counts and the market's volume reading, every number with its age. Facts by written rules, not advice."
version: 1.0.0
author: MaxOpsLabs
license: MIT
homepage: https://mapixa.gg/agents/
tags: [analysis, meme, risk, solana, mcp]
platforms: [linux, macos, windows]
prerequisites:
  commands: [curl]
required_environment_variables:
  - name: MAPIXA_TOKEN
    optional: false
    prompt: "Mapixa read-only token (app.mapixa.gg → Settings → MCP / connectors)"
    help: "https://mapixa.gg/agents/"
metadata:
  hermes:
    category: crypto
    requires_toolsets: [terminal]
    homepage: https://mapixa.gg/agents/
  mcp:
    url: https://app.mapixa.gg/mcp
    transport: streamable-http
    auth: bearer
    contract: mapixa.public.v1
---

# Mapixa: the public Solana desk over MCP

Mapixa grades the Solana coins its desk sees with one set of written rules: a grade (A, B, C or NO), the rule texts
that produced it, seven yes/no lights and the on-chain facts it read. Its MCP server gives you that public desk. You
report what the desk measured and how old the reading is. The user's own rules decide what to do with it.

## Rules

- Never tell the user to buy, sell or hold a coin, and never present a grade as a forecast. A grade is the result of
  written rules. Wherever your answer names a grade, a price or a market cap, end it with: «Facts by written rules,
  not advice.»
- Quote every number with its age. Answers carry `as_of_ms` and most carry `age_ms` (milliseconds) and `sources`.
  A block with `stale_s` is stale when its reading is older than `stale_s` seconds: say «stale» when it is.
- Time: every `*_ms` field is UTC epoch milliseconds. A time you write for a person is Basel time (Europe/Zurich)
  with its abbreviation, CET in winter and CEST in summer, day before month: «8.11. 15:54 CET». Never write «Z»,
  «UTC» or an ISO string in a sentence.
- The fourth grade arrives as the code `NIE`. Write it NO, in every language.
- The reasons are the desk's own rule texts, in Slovak (glossary below). Translate them with the glossary or quote
  them as they are; never add a reason the answer does not carry.
- A tool error (`isError: true`) says what was wrong. Fix the argument and call once more; never loop.
- Use only the five tools below. The server also lists tools for an account's own paper book; this skill does not
  call them.
- The token is a secret: keep it in the agent's secret store (for example `MAPIXA_TOKEN`), never print it, never
  paste it into a chat or a post.

## Connect

- Server: `https://app.mapixa.gg/mcp`, MCP over Streamable HTTP. `POST` one JSON-RPC message (or a batch of 1 to 20);
  the answer is `application/json`. There is no SSE stream (a `GET` with a token answers 405) and no session to keep: a
  `tools/call` works without `initialize`. Protocol versions: 2025-11-25, 2025-06-18, 2025-03-26, 2024-11-05.
- Every request needs `Authorization: Bearer <token>`. Without one the server answers 401 and a
  `WWW-Authenticate` header that points an OAuth client to its metadata.
- A token, one of two ways:
  1. Personal token: sign in at https://app.mapixa.gg (the account is free), open Settings → MCP / connectors,
     create a token and leave «paper trades too» unticked (read only). The app shows the token once. An account
     holds at most 10 live tokens; a device signed in by QR code cannot create one.
  2. OAuth 2.1: a client with discovery, dynamic client registration and PKCE needs no personal token. It gets its
     own access token by itself, starting from the 401: the person signs in and allows `read` on Mapixa's consent
     card, and the client sends that access token as the Bearer.
- Limits per account: 60 requests a minute and 2,000 a UTC day. Past a limit the answer is HTTP 429 with
  `Retry-After` in seconds: wait that long. A request body holds at most 64 KB.
- Price: free today. Paid agent access through x402 is planned and not built; no tool here asks for a payment.

## Tools

| Tool | Arguments | What it returns |
|---|---|---|
| `mapixa_desk` | `blocks` (optional): any of `calls`, `day`, `market`, `fx`, `x`, `legend` | The desk's latest graded coins (`calls.rows`: mint, symbol, venue, `verdict`, `reasons`, `lights`, `ts_ms`; `calls.total` counts all the rows, `calls.more` the rows not sent), the day's counts by grade (`day.verdicts`), the market reading (`market`), SOL/USD from Jupiter (`fx`), the sources and their freshness, the lights' legend. Omit `blocks` for the whole desk (large). |
| `mapixa_coin` | `mint` (a Solana mint address) | One coin's public card: the grade and its reasons, the shield, the facts (pool, decimals, launchpad, token program, age, mint and freeze authority), the strip and the three public chain lights. Only coins the desk has seen have a card. |
| `mapixa_health` | none | Whether the desk is fresh: `ok`, `ingest_age_s`, `last_tick_age_s`, ticks per minute. Call it before you rely on the desk. |
| `mapixa_lessons` | `lang` (optional): `en` or `sk` | The public lessons' index: id, tier, title. |
| `mapixa_lesson` | `id` (for example `Z4`), `lang` (optional) | One lesson: the claim, the body, the rule (`action`) and the sources. |

The grades: **A** = the coin meets the desk's rules · **B** = close to the rules · **C** = discovery: a coin the desk
found without a call · **NO** (`NIE`) = the shield, a safety rule, stopped it. `lights` are seven named yes/no
checks; `null` means unknown. `names_n` counts the names (callers) the desk saw on the coin.

## Example

Check the connection first (the same line as on https://mapixa.gg/agents/):

```sh
curl -s https://app.mapixa.gg/mcp \
  -H "Authorization: Bearer $MAPIXA_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"mapixa_health","arguments":{}}}'
```

Then a coin card by mint:

```sh
curl -s https://app.mapixa.gg/mcp \
  -H "Authorization: Bearer $MAPIXA_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"mapixa_coin","arguments":{"mint":"2HhH7LwfNHrxqMrSoXZ6Ri7GdmRYSJ4e8qSra9Krpump"}}}'
```

The answer is `result.structuredContent` (the same JSON as text in `result.content[0].text`). Trimmed, as production
answered on 8.11.2026 at 15:53 CET:

```json
{"contract":"mapixa.coin.v1","mint":"2HhH7LwfNHrxqMrSoXZ6Ri7GdmRYSJ4e8qSra9Krpump","symbol":"forg","verdict":"C",
 "dossier":{"reasons":["objav: coin bez callu v desku","mcap ≤ $250k ✓ · vek ≥ 10 min ✓ · nákupy 1 h ≥ 50 ✓ · objem 5 min rastie ✗"],
  "facts":{"dex_id":"pumpswap","quote_is_sol":true,"age_min":17.86,"graduated":true,"mint_authority":false,"freeze_authority":false},
  "shield":{"ok":true,"reasons":[]}},
 "as_of_ms":1794149580268,"age_ms":99213,"sources":["chain","dom"]}
```

Said for a person: «forg: grade C (discovery: a coin without a call in the desk). Market cap ≤ $250k ✓, age ≥ 10 min ✓,
buys in 1 h ≥ 50 ✓, volume over 5 min rising ✗. Mint and freeze authority off. Read 8.11. 15:53 CET, 99 s old. Facts
by written rules, not advice.»

`mapixa_desk` with `{"blocks":["day"]}` answered at 15:57 CET: `"verdicts":{"A":27,"B":369,"C":299,"NIE":558}` out of
9,383 candidates since the desk day's start (`day.start_ms`).

## Glossary of the Slovak words

| Slovak | English |
|---|---|
| objav: coin bez callu v desku | discovery: a coin without a call in the desk |
| mena: N meno / mená / mien za 60 min | names: N names (callers) in 60 min |
| call_first: nie call-first | not call-first: the desk's first trigger for this coin was not a call |
| pool: < 20 SOL | the pool holds less than 20 SOL |
| top10: top-10 drží > 40 % | the top 10 holders hold more than 40 % |
| vek | age |
| nákupy 1 h | buys in 1 hour |
| objem 5 min rastie | volume over 5 minutes is rising |
| štít | the shield (safety rules) |
| neznáme | unknown |
| `market.label`: studený · vlažný · horúci | trading volume low · medium · high (6 h) |
| `market.trend`: drží · rastie · klesá | steady · rising · falling |
| `sources`: `dom` · `chain` | read by Mapixa's own desk · read from the Solana chain |

## Contract

The public answers follow Mapixa's public contract `mapixa.public.v1` (its field list: `mapixa.public.allowlist.v1`):
a field leaves Mapixa only when the public field list names it, and every answer carries `as_of_ms` (+ `age_ms`, `sources`). The desk answers `contract:
"mapixa.desk.v1"`, a coin card `"mapixa.coin.v1"`, health `"mapixa.public.v1"`. Documentation:
https://mapixa.gg/agents/

Mapixa gives facts and grades by written rules, not advice. Crypto assets can go to zero.
