from pathlib import Path
import base64
import io
import zipfile

ROOT = Path(__file__).resolve().parent
PARTS = ROOT / "bootstrap_parts"

def restore():
    parts = sorted(PARTS.glob("part*.b64"))
    if not parts:
        raise RuntimeError("No RNT bootstrap archive parts found")
    payload = "".join(p.read_text().strip() for p in parts)
    data = base64.b64decode(payload)
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        archive.extractall(ROOT)
    print(f"RNT source restored from {len(parts)} archive parts")

if __name__ == "__main__":
    restore()
