#!/usr/bin/env python3
"""Inspect a UsePod x402 quote without paying, and build a PAYMENT-SIGNATURE envelope.

This script never touches a private key and never sends money. It does two
things:

  quote     send the request unpaid, decode the 402 PAYMENT-REQUIRED header,
            and print the rails, the cap and the body hash. Costs nothing.
  envelope  given a quote id and a signature you obtained elsewhere, print the
            base64 PAYMENT-SIGNATURE header value for the retry.

Signing belongs to the agent's wallet (e.g. the ClawPump MCP), not here.
"""
import argparse, base64, hashlib, json, os, sys, urllib.error, urllib.request

BASE = os.environ.get("USEPOD_BASE_URL", "https://api.usepod.ai")
PATH = "/proxy/x402/v1/chat/completions"


def body_hash(method: str, path: str, raw: bytes) -> str:
    """The gateway binds a quote to sha256("METHOD\\npath\\nbody")."""
    return hashlib.sha256(f"{method}\n{path}\n".encode() + raw).hexdigest()


# The gateway sits behind Cloudflare, which rejects urllib's default
# "Python-urllib/3.x" agent with a 403 (error code 1010). Always send a real one.
UA = "usepod-x402-skill/1.0"


def post(url: str, raw: bytes, headers: dict) -> tuple[int, dict, bytes]:
    req = urllib.request.Request(url, data=raw, method="POST",
                                 headers={"Content-Type": "application/json",
                                          "User-Agent": UA, **headers})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()


def cmd_quote(a) -> int:
    body = {"model": a.model, "max_tokens": a.max_tokens,
            "messages": [{"role": "user", "content": a.prompt}]}
    # Serialise once and keep the bytes: the quote is bound to these exact bytes.
    raw = json.dumps(body, separators=(",", ":")).encode()
    status, headers, payload = post(BASE + PATH, raw, {})
    print(f"status: {status}")
    print(f"body_hash (ours): {body_hash('POST', PATH, raw)}")

    hdr = next((v for k, v in headers.items() if k.lower() == "payment-required"), None)
    if status != 402 or not hdr:
        print("no PAYMENT-REQUIRED header; gateway said:")
        print(payload.decode(errors="replace")[:600])
        return 1

    q = json.loads(base64.b64decode(hdr))
    print(f"quote_id: {q.get('quote_id')}")
    for i, rail in enumerate(q.get("accepts", [])):
        print(f"\n  rail[{i}] scheme={rail.get('scheme')} network={rail.get('network')}")
        print(f"    pay_to   : {rail.get('pay_to')}")
        print(f"    asset    : {rail.get('asset')}")
        cap = rail.get("amount_microunits")
        print(f"    cap      : {cap} micro-units" + (f"  (${cap/1e6:.6f} if USDC)" if isinstance(cap, int) else ""))
        print(f"    mode     : {rail.get('mode')}")
        print(f"    expires  : {rail.get('expires_at')}")
        gw = rail.get("body_hash")
        print(f"    body_hash: {gw}  {'MATCH' if gw == body_hash('POST', PATH, raw) else 'MISMATCH'}")
    print("\nNothing was paid. A 402 costs nothing.")
    return 0


def cmd_envelope(a) -> int:
    env = {"quote_id": a.quote_id, "network": a.network, "asset": "USDC"}
    if a.proof:
        if not a.payer_wallet:
            print("--payer-wallet is required with --proof", file=sys.stderr)
            return 2
        # proof is TOP-LEVEL. The gateway's error text says payload.proof, but a
        # nested payload is ignored -- verified against the live gateway.
        env.update({"payer_wallet": a.payer_wallet, "scheme": "balance", "proof": a.proof})
        print(f"sign this exact string with {a.payer_wallet}: usepod-x402-spend:{a.quote_id}", file=sys.stderr)
    else:
        if not a.tx_signature:
            print("give either --tx-signature (on-chain) or --proof (surplus credit)", file=sys.stderr)
            return 2
        env.update({"scheme": "exact", "tx_signature": a.tx_signature})
    print(base64.b64encode(json.dumps(env, separators=(",", ":")).encode()).decode())
    return 0


p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
sub = p.add_subparsers(dest="cmd", required=True)

q = sub.add_parser("quote", help="price a request without paying")
q.add_argument("--model", default="gpt-4o-mini")
q.add_argument("--prompt", default="Reply with the single word: ok")
q.add_argument("--max-tokens", type=int, default=16, dest="max_tokens")
q.set_defaults(fn=cmd_quote)

e = sub.add_parser("envelope", help="build the PAYMENT-SIGNATURE header value")
e.add_argument("--quote-id", required=True, dest="quote_id")
e.add_argument("--network", default="solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp")
e.add_argument("--tx-signature", dest="tx_signature")
e.add_argument("--proof")
e.add_argument("--payer-wallet", dest="payer_wallet")
e.set_defaults(fn=cmd_envelope)

a = p.parse_args()
sys.exit(a.fn(a))
