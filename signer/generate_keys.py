from utils.crypto_utils import save_keypair
import os

BASE = os.path.dirname(os.path.dirname(__file__))
out_dir = os.path.join(BASE, "output")
os.makedirs(out_dir, exist_ok=True)
priv_path = os.path.join(out_dir, "ed25519_private.pem")
pub_path  = os.path.join(out_dir, "ed25519_public.pem")

if os.path.exists(priv_path) or os.path.exists(pub_path):
    print("Keys already exist. Delete them from output/ to regenerate.")
else:
    save_keypair(priv_path, pub_path)
    print("Generated keys:")
    print("  ", priv_path)
    print("  ", pub_path)