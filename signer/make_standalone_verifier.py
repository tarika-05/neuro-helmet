import os
from utils.key_export import export_public_raw_base64url

BASE = os.path.dirname(os.path.dirname(__file__))
out_dir = os.path.join(BASE, "output")
pub_pem = os.path.join(out_dir, "ed25519_public.pem")
raw_b64u_path = os.path.join(out_dir, "ed25519_public_raw.base64")
if not os.path.exists(pub_pem):
    raise SystemExit("Public key not found. Run signer/generate_keys.py first.")
export_public_raw_base64url(pub_pem, raw_b64u_path)

# inject into HTML template
tpl_path = os.path.join(BASE, "verifier_app", "static", "standalone_template.html")
with open(os.path.join(out_dir, "ed25519_public_raw.base64")) as f:
    pub_raw = f.read().strip()

with open(tpl_path) as f:
    html = f.read().replace("__PUB_RAW_B64U__", pub_raw)

out_html = os.path.join(out_dir, "standalone_verifier.html")
with open(out_html, "w") as f:
    f.write(html)

print("Standalone verifier written to:", out_html)