import os, json
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from PIL import Image
from reportlab.lib.utils import ImageReader

BASE = os.path.dirname(os.path.dirname(__file__))
out_dir = os.path.join(BASE, "output")

def make_pass(payload_path: str, token_path: str, qr_path: str, out_pdf: str):
    # Load
    with open(payload_path) as f:
        payload = json.load(f)
    with open(token_path) as f:
        token = f.read().strip()

    # Canvas
    c = canvas.Canvas(out_pdf, pagesize=A4)
    W, H = A4

    # Card background
    c.setFillColorRGB(0.07,0.09,0.11)
    c.rect(10*mm, H-70*mm, W-20*mm, 60*mm, fill=1, stroke=0)
    c.setFillColorRGB(1,1,1)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(20*mm, H-20*mm, "Smart Helmet — Offline Credential Card")

    c.setFont("Helvetica", 11)
    y = H-30*mm
    for label, key in [("Reg No", "reg_no"), ("Owner","owner"), ("Vehicle Class","vehicle_class"),
                       ("Insurance valid till","insurance_valid"), ("PUC valid till","puc_valid"), ("RC status","rc_status")]:
        val = str(payload.get(key,"—"))
        c.drawString(20*mm, y, f"{label}: {val}")
        y -= 7*mm

    # QR image
    img = Image.open(qr_path)
    qr = ImageReader(img)
    c.drawImage(qr, W-70*mm, H-65*mm, 50*mm, 50*mm, mask='auto')

    c.setFont("Helvetica-Oblique", 8)
    c.setFillColorRGB(0.8,0.8,0.8)
    c.drawString(20*mm, H-67*mm, "Show this card at checkpoints. Works offline.")

    c.showPage()
    c.save()
    return out_pdf

if __name__ == "__main__":
    # Default demo files
    payload_json = os.path.join(BASE, "demo_data", "sample_payload.json")
    token_txt = os.path.join(BASE, "output", "credential.token.txt")
    qr_png = os.path.join(BASE, "output", "credential_qr.png")
    out_pdf = os.path.join(BASE, "output", "offline_card.pdf")
    if not (os.path.exists(payload_json) and os.path.exists(token_txt) and os.path.exists(qr_png)):
        raise SystemExit("Run signer/issue_credential.py first so token/QR exist.")
    print("Writing", make_pass(payload_json, token_txt, qr_png, out_pdf))