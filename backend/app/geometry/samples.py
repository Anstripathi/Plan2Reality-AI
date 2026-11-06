"""Synthetic plans with known ground-truth dimensions (used by tests and demos)."""
from __future__ import annotations

from app.geometry.model import Floor, Opening, OpeningKind, Plan, Room, Wall

W, L = 10000.0, 8000.0          # outer dimensions
TE, TI = 300.0, 150.0           # exterior / interior wall thickness
H = 2800.0

GROUND_TRUTH = {
    "outer_width": W, "outer_length": L,
    "left_room_width": 4625.0, "right_room_width": 4625.0, "room_length": 7400.0,
    "floor_height": H,
}


def two_room_house(levels: int = 1) -> Plan:
    floors = []
    for lvl in range(levels):
        elev = lvl * H
        walls = [
            Wall("S", (TE / 2, TE / 2), (W - TE / 2, TE / 2), TE, True, TE / 2, TE / 2),
            Wall("N", (TE / 2, L - TE / 2), (W - TE / 2, L - TE / 2), TE, True, TE / 2, TE / 2),
            Wall("W", (TE / 2, TE / 2), (TE / 2, L - TE / 2), TE, True),
            Wall("E", (W - TE / 2, TE / 2), (W - TE / 2, L - TE / 2), TE, True),
            Wall("P1", (W / 2, TE), (W / 2, L - TE), TI, False),
        ]
        openings = [
            Opening("front_door", "S", 7000, 1000, 2100, 0, OpeningKind.DOOR),
            Opening("win_south", "S", 2000, 1500, 1200, 900, OpeningKind.WINDOW),
            Opening("door_inner", "P1", 3000, 900, 2100, 0, OpeningKind.DOOR),
        ]
        rooms = [
            Room("left", "Living", [(TE, TE), (W / 2 - TI / 2, TE), (W / 2 - TI / 2, L - TE), (TE, L - TE)]),
            Room("right", "Bedroom", [(W / 2 + TI / 2, TE), (W - TE, TE), (W - TE, L - TE), (W / 2 + TI / 2, L - TE)]),
        ]
        floors.append(Floor(lvl, elev, H, 150.0, walls, openings, rooms,
                            [(0, 0), (W, 0), (W, L), (0, L)]))
    return Plan("two_room_house", floors)
