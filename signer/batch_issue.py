import os, json, time
from datetime import datetime
import qrcode
from utils.crypto_utils import load_private_key, sign_compact_jws

BASE = os.path.dirname(os.path.dirname(__file__))
out_dir = os.path.join(BASE, "output")
os.makedirs(out_dir, exist_ok=True)

priv_path = os.path.join(out_dir, "ed25519_private.pem")
if not os.path.exists(priv_path):
    raise SystemExit("Private key not found. Run signer/generate_keys.py first.")

private_key = load_private_key(priv_path)

batch_input = os.path.join(BASE, "demo_data", "batch_payloads.json")
if not os.path.exists(batch_input):
    raise SystemExit("Missing demo_data/batch_payloads.json")

with open(batch_input) as f:
    items = json.load(f)

issued = []
now = int(time.time())
header_common = {"alg":"EdDSA","kid":"main-2025-08","iat":now,"nbf":now-60,"exp":now+60*60*24*3}

for i, payload in enumerate(items, start=1):
    token = sign_compact_jws(private_key, header_common, payload)
    token_fn = os.path.join(out_dir, f"token_{i}_{payload.get('reg_no','NA')}.txt")
    with open(token_fn,"w") as f: f.write(token)
    # QR
    img = qrcode.make(token)
    qr_fn = os.path.join(out_dir, f"qr_{i}_{payload.get('reg_no','NA')}.png")
    img.save(qr_fn)
    issued.append({"index":i, "token": token_fn, "qr": qr_fn})

print("Issued", len(issued), "credentials. See output/.")