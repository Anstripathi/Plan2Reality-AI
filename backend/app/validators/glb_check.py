"""Independent GLB inspector: parses the file per the glTF 2.0 spec (it does not reuse the writer)
and reports geometry back in the model's millimetre, Z-up convention."""
from __future__ import annotations

import json
import struct
from pathlib import Path


def inspect_glb(path: str | Path) -> dict:
    data = Path(path).read_bytes()
    magic, version, length = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF" or version != 2 or length != len(data):
        raise ValueError("not a valid GLB 2.0 file (header/length mismatch)")
    off, doc, bin_chunk = 12, None, b""
    while off < len(data):
        clen, ctype = struct.unpack_from("<I4s", data, off)
        body = data[off + 8: off + 8 + clen]
        if ctype == b"JSON":
            doc = json.loads(body.decode())
        elif ctype == b"BIN\x00":
            bin_chunk = body
        off += 8 + clen
    if doc is None:
        raise ValueError("GLB has no JSON chunk")
    unit = doc["asset"].get("extras", {}).get("glb_unit")
    if unit != "m":
        raise ValueError("unexpected GLB unit declaration")

    def read(acc_i):
        acc = doc["accessors"][acc_i]
        bv = doc["bufferViews"][acc["bufferView"]]
        start = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
        n = acc["count"] * (3 if acc["type"] == "VEC3" else 1)
        fmt = "<%df" % n if acc["componentType"] == 5126 else "<%dI" % n
        return struct.unpack_from(fmt, bin_chunk, start)

    nodes, g_min, g_max = [], [1e30] * 3, [-1e30] * 3
    for node in doc["nodes"]:
        prim = doc["meshes"][node["mesh"]]["primitives"][0]
        p = read(prim["attributes"]["POSITION"])
        idx = read(prim["indices"])
        verts = [(p[i] * 1000.0, -p[i + 2] * 1000.0, p[i + 1] * 1000.0) for i in range(0, len(p), 3)]
        if max(idx) >= len(verts):
            raise ValueError(f"{node['name']}: index out of range")
        vol, degenerate = 0.0, 0
        for t in range(0, len(idx), 3):
            a, b, c = verts[idx[t]], verts[idx[t + 1]], verts[idx[t + 2]]
            ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
            vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
            cx, cy, cz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
            if (cx * cx + cy * cy + cz * cz) < 1e-12:
                degenerate += 1
            vol += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
                    + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6.0
        mn = [min(v[k] for v in verts) for k in range(3)]
        mx = [max(v[k] for v in verts) for k in range(3)]
        g_min = [min(a, b) for a, b in zip(g_min, mn)]
        g_max = [max(a, b) for a, b in zip(g_max, mx)]
        nodes.append({"name": node["name"], "vertices": len(verts), "triangles": len(idx) // 3,
                      "bbox_min_mm": mn, "bbox_max_mm": mx, "volume_mm3": vol, "degenerate_triangles": degenerate})
    return {"nodes": nodes, "bbox_min_mm": g_min, "bbox_max_mm": g_max,
            "size_mm": [b - a for a, b in zip(g_min, g_max)]}
