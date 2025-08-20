from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
import base64, os

def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def export_public_raw_base64url(pem_path: str, out_path: str):
    with open(pem_path, "rb") as f:
        pub = serialization.load_pem_public_key(f.read())
    if not isinstance(pub, Ed25519PublicKey):
        raise TypeError("Public key is not Ed25519")
    raw = pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    with open(out_path, "w") as f:
        f.write(b64url(raw))
    return out_path