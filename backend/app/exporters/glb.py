"""Minimal glTF 2.0 binary writer. Source model is Z-up millimetres; GLB is Y-up metres.
Mapping (x, y, z)_mm -> (x/1000, z/1000, -y/1000) m is a proper rotation (winding preserved)."""
from __future__ import annotations

import json
import struct
from pathlib import Path

from app.reconstruction.mesh import Mesh


def _pad(b: bytes, fill: bytes) -> bytes:
    return b + fill * ((4 - len(b) % 4) % 4)


def write_glb(meshes: list[Mesh], path: str | Path, name: str = "plan2reality") -> None:
    if not meshes:
        raise ValueError("nothing to export")
    blob = bytearray()
    views, accessors, gl_meshes, nodes = [], [], [], []
    for m in meshes:
        if not m.vertices or not m.triangles:
            raise ValueError(f"mesh {m.name} is empty")
        pos = [(x / 1000.0, z / 1000.0, -y / 1000.0) for x, y, z in m.vertices]
        flat = [c for p in pos for c in p]
        pb = struct.pack(f"<{len(flat)}f", *flat)
        idx = [i for t in m.triangles for i in t]
        ib = struct.pack(f"<{len(idx)}I", *idx)
        views.append({"buffer": 0, "byteOffset": len(blob), "byteLength": len(pb), "target": 34962})
        blob += pb
        views.append({"buffer": 0, "byteOffset": len(blob), "byteLength": len(ib), "target": 34963})
        blob += ib
        mins = [min(p[k] for p in pos) for k in range(3)]
        maxs = [max(p[k] for p in pos) for k in range(3)]
        a0 = len(accessors)
        accessors.append({"bufferView": len(views) - 2, "componentType": 5126, "count": len(pos),
                          "type": "VEC3", "min": mins, "max": maxs})
        accessors.append({"bufferView": len(views) - 1, "componentType": 5125, "count": len(idx),
                          "type": "SCALAR"})
        gl_meshes.append({"name": m.name, "primitives": [{"attributes": {"POSITION": a0}, "indices": a0 + 1, "mode": 4}]})
        nodes.append({"name": m.name, "mesh": len(gl_meshes) - 1})
    doc = {
        "asset": {"version": "2.0", "generator": "Plan2Reality AI",
                  "extras": {"source_unit": "mm", "glb_unit": "m",
                             "axis_mapping": "x,y,z(Z-up mm) -> x,z,-y (Y-up m)"}},
        "scene": 0, "scenes": [{"name": name, "nodes": list(range(len(nodes)))}],
        "nodes": nodes, "meshes": gl_meshes, "accessors": accessors,
        "bufferViews": views, "buffers": [{"byteLength": len(blob)}],
    }
    js = _pad(json.dumps(doc, separators=(",", ":")).encode(), b" ")
    bn = _pad(bytes(blob), b"\x00")
    total = 12 + 8 + len(js) + 8 + len(bn)
    with open(path, "wb") as fh:
        fh.write(struct.pack("<4sII", b"glTF", 2, total))
        fh.write(struct.pack("<I4s", len(js), b"JSON") + js)
        fh.write(struct.pack("<I4s", len(bn), b"BIN\x00") + bn)
