"""Generează assets/icon.ico (siglă simplă: casă albă pe albastru) pentru .exe.

Rulează o singură dată: `python scripts/_make_icon.py`. Icoana e comisă în repo;
nu se regenerează la fiecare build. PIL e deja dependență (anexe foto în raport).
"""
from pathlib import Path

from PIL import Image, ImageDraw

S = 256
BLUE = (31, 58, 95, 255)        # albastru profesional
WHITE = (255, 255, 255, 255)

img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
d.rounded_rectangle([6, 6, S - 6, S - 6], radius=48, fill=BLUE)        # fundal rotunjit
cx = S // 2
d.polygon([(cx, 52), (54, 128), (S - 54, 128)], fill=WHITE)            # acoperiș
d.rectangle([80, 128, S - 80, 204], fill=WHITE)                       # corp casă
d.rectangle([cx - 18, 158, cx + 18, 204], fill=BLUE)                  # ușă

out = Path(__file__).resolve().parents[1] / "assets" / "icon.ico"
out.parent.mkdir(parents=True, exist_ok=True)
img.save(out, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
print(f"icon scris: {out} ({out.stat().st_size} bytes)")
