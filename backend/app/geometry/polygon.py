from __future__ import annotations

EPS = 1e-9
Point = tuple[float, float]


def signed_area(poly: list[Point]) -> float:
    s = 0.0
    for i, (x1, y1) in enumerate(poly):
        x2, y2 = poly[(i + 1) % len(poly)]
        s += x1 * y2 - x2 * y1
    return s / 2.0


def cross(a: Point, b: Point, c: Point) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _proper_intersect(p1: Point, p2: Point, p3: Point, p4: Point) -> bool:
    d1, d2 = cross(p3, p4, p1), cross(p3, p4, p2)
    d3, d4 = cross(p1, p2, p3), cross(p1, p2, p4)
    return ((d1 > EPS and d2 < -EPS) or (d1 < -EPS and d2 > EPS)) and \
           ((d3 > EPS and d4 < -EPS) or (d3 < -EPS and d4 > EPS))


def is_simple(poly: list[Point]) -> bool:
    n = len(poly)
    if n < 3:
        return False
    for i in range(n):
        for j in range(i + 1, n):
            if j == i + 1 or (i == 0 and j == n - 1):
                continue
            if _proper_intersect(poly[i], poly[(i + 1) % n], poly[j], poly[(j + 1) % n]):
                return False
    return abs(signed_area(poly)) > EPS


def _in_tri(p: Point, a: Point, b: Point, c: Point) -> bool:
    return cross(a, b, p) >= -EPS and cross(b, c, p) >= -EPS and cross(c, a, p) >= -EPS


def triangulate(poly: list[Point]) -> tuple[list[Point], list[tuple[int, int, int]]]:
    """Ear clipping. Returns (CCW-ordered points, triangles indexing them)."""
    if len(poly) < 3:
        raise ValueError("polygon needs at least 3 points")
    if not is_simple(poly):
        raise ValueError("cannot triangulate: polygon is not simple")
    pts = list(poly) if signed_area(poly) > 0 else list(reversed(poly))
    idx = list(range(len(pts)))
    tris: list[tuple[int, int, int]] = []
    while len(idx) > 3:
        for k in range(len(idx)):
            i0, i1, i2 = idx[k - 1], idx[k], idx[(k + 1) % len(idx)]
            a, b, c = pts[i0], pts[i1], pts[i2]
            cr = cross(a, b, c)
            if abs(cr) <= EPS:            # collinear vertex: drop it
                idx.pop(k)
                break
            if cr < 0:
                continue                   # reflex
            if any(_in_tri(pts[j], a, b, c) and pts[j] not in (a, b, c)
                   for j in idx if j not in (i0, i1, i2)):
                continue
            tris.append((i0, i1, i2))
            idx.pop(k)
            break
        else:
            raise ValueError("cannot triangulate: polygon is not simple")
    if abs(cross(pts[idx[0]], pts[idx[1]], pts[idx[2]])) > EPS:
        tris.append((idx[0], idx[1], idx[2]))
    return pts, tris
