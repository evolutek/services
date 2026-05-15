"""Camera + ArUco perception, ported from evo_lib for the legacy services stack.

Source of truth: evo_hl_omnissiah/library/src/evo_lib/{drivers/camera,perception,interfaces}.
This is a Python 3.11-compatible extraction. Keep API surface in sync with upstream
when possible; runtime concurrency primitives (Task, Logger) were replaced with
stdlib equivalents (synchronous calls, logging module).
"""

from evolutek.lib.vision.markers import (
    DEFAULT_ARUCO_DICTIONARY,
    DEFAULT_CHARUCO_MARKER_MM,
    DEFAULT_CHARUCO_SQUARE_MM,
    DEFAULT_CHARUCO_SQUARES_X,
    DEFAULT_CHARUCO_SQUARES_Y,
    ArucoMarker,
)
from evolutek.lib.vision.aruco import (
    ArucoState,
    CharucoCalibrationSession,
)
from evolutek.lib.vision.uvc import (
    DEFAULT_FOURCC,
    DEFAULT_HEIGHT,
    DEFAULT_READER_FPS,
    DEFAULT_WIDTH,
    UvcCamera,
)
from evolutek.lib.vision.eurobot_tags import (
    EUROBOT_FIXED_TABLE_TAGS,
    EUROBOT_TAG_SIZES_MM,
)

__all__ = [
    "ArucoMarker",
    "ArucoState",
    "CharucoCalibrationSession",
    "UvcCamera",
    "EUROBOT_FIXED_TABLE_TAGS",
    "EUROBOT_TAG_SIZES_MM",
    "DEFAULT_ARUCO_DICTIONARY",
    "DEFAULT_CHARUCO_MARKER_MM",
    "DEFAULT_CHARUCO_SQUARE_MM",
    "DEFAULT_CHARUCO_SQUARES_X",
    "DEFAULT_CHARUCO_SQUARES_Y",
    "DEFAULT_FOURCC",
    "DEFAULT_HEIGHT",
    "DEFAULT_READER_FPS",
    "DEFAULT_WIDTH",
]
