import json, time, os
from datetime import datetime, timedelta
import qrcode
from utils.crypto_utils import load_private_key, sign_compact_jws

BASE = os.path.dirname(os.path.dirname(__file__))
out_dir = os.path.join(BASE, "output")
os.makedirs(out_dir, exist_ok=True)

priv_path = os.path.join(out_dir, "ed25519_private.pem")
if not os.path.exists(priv_path):
    raise SystemExit("Private key not found. Run signer/generate_keys.py first.")

# Load sample payload
with open(os.path.join(BASE, "demo_data", "sample_payload.json")) as f:
    payload = json.load(f)

# Header with validity window (offline-friendly)
iat = int(time.time())
nbf = iat - 60
exp = iat + 60*60*24*3  # 72 hours validity window for the credential
header = {
    "alg": "EdDSA",
    "kid": "main-2025-08",
    "iat": iat,
    "nbf": nbf,
    "exp": exp
}

private_key = load_private_key(priv_path)
token = sign_compact_jws(private_key, header, payload)

# Save token and QR
token_path = os.path.join(out_dir, "credential.token.txt")
with open(token_path,"w") as f:
    f.write(token)

# Also save a JSON envelope
envelope = {"token": token}
json_path = os.path.join(out_dir, "credential_envelope.json")
with open(json_path,"w") as f:
    json.dump(envelope, f, indent=2)

# QR code
img = qrcode.make(token)
qr_path = os.path.join(out_dir, "credential_qr.png")
img.save(qr_path)

print("Issued offline credential:")
print("  Token:", token_path)
print("  Envelope:", json_path)
print("  QR:", qr_path)