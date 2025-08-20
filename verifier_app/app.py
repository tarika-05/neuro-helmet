import os, io, json, datetime
from flask import Flask, render_template, request, redirect, url_for
import cv2
from utils.crypto_utils import load_public_key, verify_compact_jws

BASE = os.path.dirname(os.path.dirname(__file__))
out_dir = os.path.join(BASE, "output")
pub_path  = os.path.join(out_dir, "ed25519_public.pem")
if not os.path.exists(pub_path):
    raise SystemExit("Public key not found. Run signer/generate_keys.py to create keys.")

app = Flask(__name__)
public_key = load_public_key(pub_path)

def decode_qr_from_image(file_storage):
    # Read image bytes into OpenCV
    file_bytes = file_storage.read()
    img_array = bytearray(file_bytes)
    import numpy as np
    nparr = np.asarray(img_array, dtype=np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    detector = cv2.QRCodeDetector()
    data, points, _ = detector.detectAndDecode(img)
    return data if data else None

def check_document_expiries(payload: dict):
    reasons = []
    # simple date checks if present
    for key in ["insurance_valid","puc_valid"]:
        if key in payload:
            try:
                exp = datetime.datetime.strptime(payload[key], "%Y-%m-%d").date()
                if exp < datetime.date.today():
                    reasons.append(f"{key} expired on {exp.isoformat()}")
            except Exception:
                reasons.append(f"{key} has invalid date format")
    if payload.get("rc_status") and str(payload["rc_status"]).upper() != "ACTIVE":
        reasons.append(f"RC status is {payload['rc_status']}")
    return reasons

@app.route("/", methods=["GET","POST"])
def index():
    result = None
    token_text = ""
    reasons = []
    header = {}
    payload = {}
    if request.method == "POST":
        token_text = request.form.get("token","").strip()
        if not token_text and "qr_image" in request.files:
            token_text = decode_qr_from_image(request.files["qr_image"]) or ""
        ok, msg, header, payload = verify_compact_jws(public_key, token_text)
        if ok:
            # additional domain checks
            reasons = check_document_expiries(payload)
            if reasons:
                result = f"❌ INVALID: {', '.join(reasons)}"
            else:
                result = "✅ VALID: All checks passed"
        else:
            result = f"❌ INVALID: {msg}"
    return render_template("index.html", result=result, token_text=token_text, header=header, payload=payload, reasons=reasons)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)