"""ArUco marker dataclass + ChArUco/dictionary defaults.

Extracted from evo_lib.interfaces.camera. The original file also defined
a Camera ABC with REPL command bindings (DriverCommands/ArgTypes) — those
are dropped here because the legacy cellaserv stack does not use them.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np


DEFAULT_ARUCO_DICTIONARY = "DICT_4X4_100"
DEFAULT_CHARUCO_SQUARES_X = 5
DEFAULT_CHARUCO_SQUARES_Y = 5
DEFAULT_CHARUCO_SQUARE_MM = 40.0
DEFAULT_CHARUCO_MARKER_MM = 32.0


@dataclass(slots=True)
class ArucoMarker:
    id: int
    corners: "np.ndarray"
    rvec_camera: "np.ndarray | None" = None
    tvec_camera: "np.ndarray | None" = None
    position_robot_mm: "np.ndarray | None" = None
    # (qw, qx, qy, qz) — full rotation; needed for tilted markers where yaw alone loses info.
    quat_robot: "tuple[float, float, float, float] | None" = None
    yaw_robot_rad: "float | None" = None
    source_camera: "str | None" = None
