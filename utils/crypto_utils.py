import json, base64, time
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization

def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def b64url_decode(s: str) -> bytes:
    pad = "=" * ((4 - len(s) % 4) % 4)
    return base64.urlsafe_b64decode(s + pad)

def load_private_key(pem_path: str) -> Ed25519PrivateKey:
    with open(pem_path,"rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)

def load_public_key(pem_path: str) -> Ed25519PublicKey:
    with open(pem_path,"rb") as f:
        return serialization.load_pem_public_key(f.read())

def save_keypair(priv_path: str, pub_path: str):
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    priv_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    pub_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open(priv_path,"wb") as f: f.write(priv_pem)
    with open(pub_path,"wb") as f: f.write(pub_pem)

def sign_compact_jws(private_key: Ed25519PrivateKey, header: dict, payload: dict) -> str:
    # Compact JWS-like: BASE64URL(header) + '.' + BASE64URL(payload) + '.' + BASE64URL(signature)
    h = json.dumps(header, separators=(",",":"), sort_keys=True).encode()
    p = json.dumps(payload, separators=(",",":"), sort_keys=True).encode()
    signing_input = b".".join([b64url(h).encode(), b64url(p).encode()])
    signature = private_key.sign(signing_input)
    return ".".join([b64url(h), b64url(p), b64url(signature)])

def verify_compact_jws(public_key: Ed25519PublicKey, token: str):
    parts = token.split(".")
    if len(parts) != 3:
        return False, "Invalid token format", None, None
    h_b, p_b, s_b = parts
    try:
        h = json.loads(b64url_decode(h_b))
        p = json.loads(b64url_decode(p_b))
        signing_input = ".".join([h_b, p_b]).encode()
        sig = b64url_decode(s_b)
        public_key.verify(sig, signing_input)
    except Exception as e:
        return False, f"Signature verification failed: {e}", None, None
    # Temporal checks (nbf/exp)
    now = int(time.time())
    if "nbf" in h and now < int(h["nbf"]):
        return False, "Token not yet valid (nbf)", h, p
    if "exp" in h and now > int(h["exp"]):
        return False, "Token expired (exp)", h, p
    return True, "OK", h, p