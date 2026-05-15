"""Canonical Eurobot ArUco tag definitions (positions and sizes).

Frame: Evolutek table/robot. Centers from FINAL_1.0_playmat/table.svg.
All four fixed tags share yaw = +pi/2 (motif X axis points toward +Y).

Sizes per the Eurobot general rules + 2026 specific rules:
  - 1-10  : robot identification markers on beacon support (70mm)
  - 20-23 : fixed playmat tags (100mm)
  - 36,47 : crates of nuts, blue/yellow team (30mm)
  - 41    : empty crates (30mm)

Ported from evo_hl_omnissiah/src/evo_robot/perception/eurobot_tags.py.
Pose3D dropped — fixed-tag poses are exposed as (x_mm, y_mm, z_mm, yaw_rad)
tuples since the legacy stack does not pull in the full Pose3D type.
"""

import math

# (x_mm, y_mm, z_mm, yaw_rad). Tilt (roll, pitch) is zero for fixed playmat tags.
EUROBOT_FIXED_TABLE_TAGS: "dict[int, tuple[float, float, float, float]]" = {
    20: (600.0, -900.0, 0.0, math.pi / 2),
    21: (600.0, 900.0, 0.0, math.pi / 2),
    22: (1400.0, -900.0, 0.0, math.pi / 2),
    23: (1400.0, 900.0, 0.0, math.pi / 2),
}


EUROBOT_TAG_SIZES_MM: dict[int, float] = {
    **{i: 70.0 for i in range(1, 11)},
    **{i: 100.0 for i in (20, 21, 22, 23)},
    36: 30.0,
    41: 30.0,
    47: 30.0,
}
