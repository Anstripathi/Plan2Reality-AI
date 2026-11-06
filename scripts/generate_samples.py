"""Regenerate samples/two_room_house/*  (run from repo root: python scripts/generate_samples.py)."""
import json, sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "backend"))
import cv2, numpy as np
from app.exporters.glb import write_glb
from app.geometry.samples import GROUND_TRUTH, two_room_house
from app.reconstruction.builder import build_plan
from app.validators.glb_check import inspect_glb

out = root / "samples" / "two_room_house"
out.mkdir(parents=True, exist_ok=True)
plan = two_room_house()
(out / "plan.json").write_text(plan.to_json())
(out / "ground_truth.json").write_text(json.dumps({"unit": "mm", **GROUND_TRUTH}, indent=2))
write_glb(build_plan(plan), out / "model.glb")
rep = inspect_glb(out / "model.glb")
(out / "model_report.json").write_text(json.dumps(rep, indent=2))

img = np.full((1000, 1400), 255, np.uint8)            # 10 mm per pixel; 100 px scale bar = 1000 mm
cv2.rectangle(img, (200, 200), (1200, 800), 0, 12)
cv2.rectangle(img, (600, 200), (606, 800), 0, -1)
cv2.line(img, (200, 900), (300, 900), 0, 4)
cv2.line(img, (200, 890), (200, 910), 0, 4)
cv2.line(img, (300, 890), (300, 910), 0, 4)
cv2.imwrite(str(out / "plan_raster.png"), img)
(out / "README.md").write_text(
    "Synthetic sample with known dimensions.\n\n"
    "- plan.json: 2D geometry (mm). ground_truth.json: true dimensions.\n"
    "- model.glb: generated 3D model; model_report.json: independent re-read of it.\n"
    "- plan_raster.png: drawn raster test image, 10 mm per pixel (scale bar = 100 px = 1000 mm). "
    "Not a real scanned plan.\n")
print("size_mm", rep["size_mm"])
