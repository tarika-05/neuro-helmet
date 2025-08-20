# Offline Helmet Documents — Hackathon Prototype (Software‑Only)

This project demonstrates **offline verification of rider/vehicle documents** using a compact, digitally‑signed credential.
It works without internet and without RFID/NFC hardware for the demo. You can show the token as text or as a QR image.

## Features
- Ed25519 digital signatures (compact JWS‑style token)
- Issue a credential from sample payload (RC/insurance/PUC validity)
- Generate a QR containing the credential
- Verify **offline** (Flask app) via pasted token or uploaded QR image
- Domain checks for expiries (insurance/PUC) and RC status

## Project Structure
```
offline-helmet-docs/
  signer/
    generate_keys.py        # create Ed25519 keypair
    issue_credential.py     # build and sign credential, generate QR
  verifier_app/
    app.py                  # offline verifier (Flask)
    templates/index.html
    static/style.css
  utils/
    crypto_utils.py         # sign/verify helpers
  demo_data/sample_payload.json
  output/                   # keys, token, QR output
  requirements.txt
```

## Quick Start

1) Create a virtualenv and install deps
```bash
cd offline-helmet-docs
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

2) Generate keys
```bash
python signer/generate_keys.py
```

3) Issue a credential (and QR)
```bash
python signer/issue_credential.py
# Outputs files in output/:
#  - ed25519_private.pem
#  - ed25519_public.pem
#  - credential.token.txt
#  - credential_envelope.json
#  - credential_qr.png
```

4) Run verifier (works offline)
```bash
python verifier_app/app.py
# Open http://localhost:8000
# Paste the token from output/credential.token.txt OR upload output/credential_qr.png
```

## How It Works (High Level)
- We encode a **header** (algorithm + validity window) and a **payload** (document status).
- We sign `BASE64URL(header) + '.' + BASE64URL(payload)` with Ed25519.
- The verifier checks the signature **locally** and applies expiry rules.
- All of this works offline; internet is not required at verification time.

## Notes
- For production, store **only proofs/hashes** in the credential; fetch full docs when online.
- Rotate keys regularly and protect the private key inside an HSM.
- The QR contains the **signed token**. Anyone can read it, but only you can **sign** valid tokens.

---

## New Goodies for Demo-Ready Project

### Standalone Browser Verifier (no server)
- Generate a static HTML file that verifies tokens **fully offline** in the browser.
- After generating keys:
  ```bash
  python signer/make_standalone_verifier.py
  # -> open output/standalone_verifier.html in any modern browser
  ```

### Batch Issuer
  ```bash
  # Prepare demo_data/batch_payloads.json then:
  python signer/batch_issue.py
  # -> writes multiple tokens + QRs into output/
  ```

### Printable PDF Pass
  ```bash
  # After issuing a credential:
  python printing/make_pass.py
  # -> output/offline_card.pdf (print & carry)
  ```

