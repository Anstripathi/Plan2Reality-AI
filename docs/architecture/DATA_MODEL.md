# Data model
`Plan` -> `Floor(level, elevation_mm, height_mm, slab_thickness_mm)` -> `Wall` (centerline, thickness, optional end extensions), `Opening` (wall_id, offset along centerline, width, height, sill, kind), `Room` (polygon), `footprint` polygon. All millimetres, Z up. JSON round-trip via `Plan.to_json/from_json`.
Dimensions are `Measurement` objects (provenance, confidence, original value/unit); `DimensionCheck` compares them with reconstructed values.
GLB: Y-up metres; mapping (x,y,z) -> (x/1000, z/1000, -y/1000), declared in asset extras.
