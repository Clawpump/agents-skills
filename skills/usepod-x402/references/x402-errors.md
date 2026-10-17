# UsePod x402 errors — observed against the live gateway

Endpoint: `POST https://api.usepod.ai/proxy/x402/v1/chat/completions`  
Captured: 2026-09-18T19:50Z, plus a paid spike on 2026-09-25.

**Provenance** is stated per row. *observed* = returned by the live gateway to a real probe.
*assumed* = not yet seen live; listed so a client can handle it, not as fact.

| Error | Status | Provenance | Message |
|---|---|---|---|
| `invalid_json_body` | 400 | observed | bad request: invalid JSON: expected ident at line 1 column 2 |
| `missing_max_tokens` | 400 | observed | bad request: x402 requests must include max_tokens or max_completion_tokens |
| `stream_not_supported` | 400 | observed | bad request: x402 tokenless streaming is not enabled; use an MPP session |
| `no_provider` | 503 | observed | no healthy provider for model: {model} |
| `invalid_payment_json` | 400 | observed | bad request: invalid payment header JSON: expected ident at line 1 column 2 |
| `missing_tx_signature` | 400 | observed | bad request: PAYMENT-SIGNATURE is missing the Solana transaction signature |
| `unknown_quote` | 400 | observed | bad request: unknown x402 quote |
| `unsupported_network` | 400 | observed | bad request: only Solana and Base x402 payments are supported |
| `tx_not_found` | 400 | observed | bad request: Solana transaction not found or not yet confirmed |
| `quote_mismatch` | 400 | observed (phase-0 probe) | bad request: x402 quote does not match this request |
| `balance_missing_proof` | 400 | observed | bad request: balance spend requires payload.proof (signed quote id) |
| `balance_missing_payer` | 400 | observed | bad request: balance spend requires payer_wallet |
| `balance_proof_malformed` | 400 | observed | bad request: proof is not a 64-byte ed25519 signature |
| `balance_proof_invalid` | 400 | observed | bad request: proof signature does not verify for payer_wallet |
| `balance_insufficient` | 400 | observed | bad request: x402 wallet balance is below the quote cap ({cap} microunits); pay on-chain instead |
| `quote_expired` | 400 | assumed | bad request: x402 quote expired |
| `signature_replayed` | 400 | assumed | bad request: transaction signature already used for another quote |
| `underpaid` | 400 | assumed | bad request: payment is below the quoted amount |

## Notes from the paid spike (2026-09-25)

- A settled payment returns `PAYMENT-RESPONSE` with `payer`, `status`, `network`,
  `success`, `quote_id`, `payment_id`, `x402_version`, `max_microunits` and
  `charged_microunits`. It does **not** echo the transaction signature — keep your own.
- The settled response also carries `x-pod-route` and `x-pod-provider-id`, which is
  the only way to learn which provider served the call.
- `balance_insufficient` names the shortfall in micro-units and tells you to pay
  on-chain. Nothing is spent when it fires, so treat it as routine fallback.
- Paying above the quoted cap is not credited and not refunded.
