"""ArUco detection + ChArUco calibration — independent of any specific camera driver.

Ported as-is from evo_lib.perception.aruco; the only edit is the local
import path for ArucoMarker. No PEP 695 syntax, no Task/Logger plumbing,
no external dependency beyond cv2/numpy/json5 — runs on Python 3.11+.
"""

from __future__ import annotations

import datetime
import os
from typing import TYPE_CHECKING, Any

from evolutek.lib.vision.markers import ArucoMarker

if TYPE_CHECKING:
    import numpy as np


DEFAULT_RMS_THRESHOLD_PX = 0.5
DEFAULT_PER_VIEW_REJECT_PX = 1.5


def _aruco_dict_from_name(name: str) -> Any:
    import cv2

    full_name = name if name.startswith("DICT_") else f"DICT_{name}"
    if not hasattr(cv2.aruco, full_name):
        raise ValueError(f"Unknown ArUco dictionary: {name}")
    return cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, full_name))


def _build_charuco_board(
    squares_x: int,
    squares_y: int,
    square_mm: float,
    marker_mm: float,
    dictionary_name: str,
) -> Any:
    import cv2

    dictionary = _aruco_dict_from_name(dictionary_name)
    return cv2.aruco.CharucoBoard((squares_x, squares_y), square_mm, marker_mm, dictionary)


def _marker_object_points(marker_mm: float) -> "np.ndarray":
    import numpy as np

    half = marker_mm * 0.5
    return np.array(
        [
            [-half, half, 0.0],
            [half, half, 0.0],
            [half, -half, 0.0],
            [-half, -half, 0.0],
        ],
        dtype=np.float32,
    )


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def _rot_to_quat(R: "np.ndarray") -> tuple[float, float, float, float]:
    """3x3 rotation matrix to (qw, qx, qy, qz) unit quaternion (Shepperd's method)."""
    import numpy as np

    trace = R[0, 0] + R[1, 1] + R[2, 2]
    if trace > 0.0:
        s = 2.0 * np.sqrt(1.0 + trace)
        return (
            float(0.25 * s),
            float((R[2, 1] - R[1, 2]) / s),
            float((R[0, 2] - R[2, 0]) / s),
            float((R[1, 0] - R[0, 1]) / s),
        )
    if R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:
        s = 2.0 * np.sqrt(1.0 + R[0, 0] - R[1, 1] - R[2, 2])
        return (
            float((R[2, 1] - R[1, 2]) / s),
            float(0.25 * s),
            float((R[0, 1] + R[1, 0]) / s),
            float((R[0, 2] + R[2, 0]) / s),
        )
    if R[1, 1] > R[2, 2]:
        s = 2.0 * np.sqrt(1.0 + R[1, 1] - R[0, 0] - R[2, 2])
        return (
            float((R[0, 2] - R[2, 0]) / s),
            float((R[0, 1] + R[1, 0]) / s),
            float(0.25 * s),
            float((R[1, 2] + R[2, 1]) / s),
        )
    s = 2.0 * np.sqrt(1.0 + R[2, 2] - R[0, 0] - R[1, 1])
    return (
        float((R[1, 0] - R[0, 1]) / s),
        float((R[0, 2] + R[2, 0]) / s),
        float((R[1, 2] + R[2, 1]) / s),
        float(0.25 * s),
    )


class CharucoCalibrationSession:
    """Stateful collector for ChArUco views, decoupled from any Peripheral."""

    def __init__(
        self,
        board: Any,
        dictionary: Any,
        rms_threshold_px: float = DEFAULT_RMS_THRESHOLD_PX,
        per_view_reject_px: float = DEFAULT_PER_VIEW_REJECT_PX,
    ):
        self._board = board
        self._dictionary = dictionary
        self._rms_threshold = rms_threshold_px
        self._per_view_reject = per_view_reject_px
        self._all_corners: list[Any] = []
        self._all_ids: list[Any] = []
        self._image_size: tuple[int, int] | None = None
        self._detector: Any = None

    @property
    def view_count(self) -> int:
        return len(self._all_corners)

    def capture_view(self, gray_frame: "np.ndarray") -> int:
        import cv2

        if self._image_size is None:
            h, w = gray_frame.shape[:2]
            self._image_size = (w, h)

        if self._detector is None:
            self._detector = cv2.aruco.ArucoDetector(
                self._dictionary, cv2.aruco.DetectorParameters()
            )
        marker_corners, marker_ids, _ = self._detector.detectMarkers(gray_frame)
        if marker_ids is None or len(marker_ids) == 0:
            return 0

        ret, charuco_corners, charuco_ids = cv2.aruco.interpolateCornersCharuco(
            marker_corners, marker_ids, gray_frame, self._board
        )
        if ret <= 0 or charuco_corners is None or charuco_ids is None:
            return 0

        self._all_corners.append(charuco_corners)
        self._all_ids.append(charuco_ids)
        return int(ret)

    def compute(self) -> dict[str, Any]:
        import cv2
        import numpy as np

        if self._image_size is None:
            raise RuntimeError("No views captured; nothing to calibrate.")
        if len(self._all_corners) < 4:
            raise RuntimeError(f"Only {len(self._all_corners)} views captured; need at least 4.")

        rms, K, dist, rvecs, tvecs, std_intr, std_extr, per_view = (
            cv2.aruco.calibrateCameraCharucoExtended(
                charucoCorners=self._all_corners,
                charucoIds=self._all_ids,
                board=self._board,
                imageSize=self._image_size,
                cameraMatrix=None,
                distCoeffs=None,
            )
        )

        per_view_arr = np.asarray(per_view).reshape(-1)
        keep_mask = per_view_arr <= self._per_view_reject
        n_drop = int(np.size(keep_mask) - np.sum(keep_mask))
        if n_drop > 0 and np.sum(keep_mask) >= 4:
            kept_corners = [c for c, k in zip(self._all_corners, keep_mask) if k]
            kept_ids = [i for i, k in zip(self._all_ids, keep_mask) if k]
            rms, K, dist, rvecs, tvecs, std_intr, std_extr, per_view = (
                cv2.aruco.calibrateCameraCharucoExtended(
                    charucoCorners=kept_corners,
                    charucoIds=kept_ids,
                    board=self._board,
                    imageSize=self._image_size,
                    cameraMatrix=None,
                    distCoeffs=None,
                )
            )

        if rms > self._rms_threshold:
            raise RuntimeError(
                f"Calibration RMS {rms:.3f}px exceeds threshold "
                f"{self._rms_threshold:.3f}px (kept {len(self._all_corners) - n_drop} views, "
                f"dropped {n_drop}); capture more or steadier views."
            )

        return {
            "K": K.flatten().tolist(),
            "dist": dist.flatten().tolist(),
            "image_size": list(self._image_size),
            "rms": float(rms),
            "n_views_used": int(len(self._all_corners) - n_drop),
            "n_views_dropped": int(n_drop),
            "captured_at": _now_iso(),
        }


class ArucoState:
    """Detection + calibration state, shared by any camera driver implementation."""

    def __init__(
        self,
        marker_size_mm: float,
        dictionary: str,
        charuco_squares_x: int,
        charuco_squares_y: int,
        charuco_square_mm: float,
        charuco_marker_mm: float,
        calibration_path: "str | None",
        tag_sizes_mm: "dict[int, float] | None" = None,
    ):
        self.marker_size_mm = marker_size_mm
        self.dictionary_name = dictionary
        self.charuco_geom = (
            charuco_squares_x,
            charuco_squares_y,
            charuco_square_mm,
            charuco_marker_mm,
        )
        self.calibration_path = calibration_path
        # Per-id marker size lookup; defaults to marker_size_mm when unset. The
        # application layer owns domain tables like Eurobot's (see eurobot_tags.py).
        self.tag_sizes_mm: dict[int, float] = dict(tag_sizes_mm) if tag_sizes_mm else {}
        self.K = None
        self.dist = None
        self.image_size: "tuple[int, int] | None" = None
        self.R_robot_camera = None
        self.t_robot_camera = None
        self._obj_pts_cache: "dict[float, np.ndarray]" = {
            marker_size_mm: _marker_object_points(marker_size_mm)
        }
        self._detector_handle = None

    def _obj_pts_for(self, size_mm: float) -> "np.ndarray":
        cached = self._obj_pts_cache.get(size_mm)
        if cached is None:
            cached = _marker_object_points(size_mm)
            self._obj_pts_cache[size_mm] = cached
        return cached

    def _size_for_id(self, marker_id: int) -> float:
        return self.tag_sizes_mm.get(marker_id, self.marker_size_mm)

    def detector(self) -> Any:
        import cv2

        if self._detector_handle is None:
            dictionary = _aruco_dict_from_name(self.dictionary_name)
            self._detector_handle = cv2.aruco.ArucoDetector(
                dictionary, cv2.aruco.DetectorParameters()
            )
        return self._detector_handle

    def detect_in_frame(self, frame: "np.ndarray") -> list[ArucoMarker]:
        import cv2
        import numpy as np

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if frame.ndim == 3 else frame
        marker_corners, marker_ids, _ = self.detector().detectMarkers(gray)
        if marker_ids is None or len(marker_ids) == 0:
            return []

        results: list[ArucoMarker] = []
        for i, marker_id in enumerate(marker_ids.flatten()):
            corners_ij = marker_corners[i].reshape(4, 2).astype(np.float32)
            mid = int(marker_id)
            marker = ArucoMarker(id=mid, corners=corners_ij)
            if self.K is not None and self.dist is not None:
                obj_pts = self._obj_pts_for(self._size_for_id(mid))
                ok, rvec, tvec = cv2.solvePnP(
                    obj_pts,
                    corners_ij,
                    self.K,
                    self.dist,
                    flags=cv2.SOLVEPNP_IPPE_SQUARE,
                )
                if ok:
                    marker.rvec_camera = rvec.reshape(3)
                    marker.tvec_camera = tvec.reshape(3)
                    if self.R_robot_camera is not None and self.t_robot_camera is not None:
                        pos_robot = self.R_robot_camera @ marker.tvec_camera.reshape(
                            3, 1
                        ) + self.t_robot_camera.reshape(3, 1)
                        marker.position_robot_mm = pos_robot.reshape(3)
                        R_camera_marker, _ = cv2.Rodrigues(rvec)
                        R_robot_marker = self.R_robot_camera @ R_camera_marker
                        qw, qx, qy, qz = _rot_to_quat(R_robot_marker)
                        marker.quat_robot = (qw, qx, qy, qz)
                        siny = 2.0 * (qw * qz + qx * qy)
                        cosy = 1.0 - 2.0 * (qy * qy + qz * qz)
                        marker.yaw_robot_rad = float(np.arctan2(siny, cosy))
            results.append(marker)
        return results

    def calibration_session(self) -> CharucoCalibrationSession:
        sx, sy, sq_mm, mk_mm = self.charuco_geom
        board = _build_charuco_board(sx, sy, sq_mm, mk_mm, self.dictionary_name)
        dictionary = _aruco_dict_from_name(self.dictionary_name)
        return CharucoCalibrationSession(board=board, dictionary=dictionary)

    def apply_intrinsics(self, intrinsics: dict[str, Any]) -> None:
        import numpy as np

        self.K = np.asarray(intrinsics["K"], dtype=np.float64).reshape(3, 3)
        self.dist = np.asarray(intrinsics["dist"], dtype=np.float64).reshape(-1)
        self.image_size = tuple(intrinsics["image_size"])

    def is_intrinsics_loaded(self) -> bool:
        return self.K is not None and self.dist is not None

    def is_extrinsics_loaded(self) -> bool:
        return self.R_robot_camera is not None and self.t_robot_camera is not None

    def calibrate_extrinsics(
        self,
        markers: list[ArucoMarker],
        reference_marker_id: int,
        R_robot_marker: "np.ndarray",
        t_robot_marker_mm: "np.ndarray",
    ) -> dict[str, Any]:
        import cv2
        import numpy as np

        if self.K is None or self.dist is None:
            raise RuntimeError("Cannot calibrate extrinsics without intrinsics first.")

        target = next((m for m in markers if m.id == reference_marker_id), None)
        if target is None or target.rvec_camera is None or target.tvec_camera is None:
            raise RuntimeError(
                f"Reference marker {reference_marker_id} not visible "
                f"(detected ids: {[m.id for m in markers]})"
            )

        # Rotation matrices are orthonormal so R^-1 = R^T (no expensive inverse).
        R_camera_marker, _ = cv2.Rodrigues(target.rvec_camera.reshape(3, 1))
        t_camera_marker = target.tvec_camera.reshape(3, 1)
        R_marker_camera = R_camera_marker.T
        t_marker_camera = -R_marker_camera @ t_camera_marker

        R_robot_camera = np.asarray(R_robot_marker) @ R_marker_camera
        t_robot_camera = np.asarray(R_robot_marker) @ t_marker_camera + np.asarray(
            t_robot_marker_mm
        ).reshape(3, 1)

        self.R_robot_camera = R_robot_camera
        self.t_robot_camera = t_robot_camera

        return {
            "R_robot_camera": R_robot_camera.flatten().tolist(),
            "t_robot_camera_mm": t_robot_camera.flatten().tolist(),
            "reference_marker_id": int(reference_marker_id),
            "captured_at": _now_iso(),
        }

    def load(self, path: "str | None" = None) -> bool:
        target = path or self.calibration_path
        if target is None or not os.path.exists(target):
            return False

        import json5
        import numpy as np

        with open(target, "r") as f:
            data = json5.load(f)

        intr = data.get("intrinsics")
        if intr is not None:
            self.K = np.asarray(intr["K"], dtype=np.float64).reshape(3, 3)
            self.dist = np.asarray(intr["dist"], dtype=np.float64).reshape(-1)
            self.image_size = tuple(intr.get("image_size", (0, 0)))

        # Accept R_world_camera / t_world_camera_mm for robots calibrated before the rename.
        extr = data.get("extrinsics")
        if extr is not None:
            R_key = "R_robot_camera" if "R_robot_camera" in extr else "R_world_camera"
            t_key = "t_robot_camera_mm" if "t_robot_camera_mm" in extr else "t_world_camera_mm"
            self.R_robot_camera = np.asarray(extr[R_key], dtype=np.float64).reshape(3, 3)
            self.t_robot_camera = np.asarray(extr[t_key], dtype=np.float64).reshape(3)
        return intr is not None or extr is not None

    def save(self, path: "str | None" = None) -> str:
        target = path or self.calibration_path
        if target is None:
            raise RuntimeError("no calibration_path configured")

        import json5

        parent = os.path.dirname(target)
        if parent:
            os.makedirs(parent, exist_ok=True)
        payload: dict[str, Any] = {}
        if self.K is not None and self.dist is not None:
            payload["intrinsics"] = {
                "K": self.K.flatten().tolist(),
                "dist": self.dist.flatten().tolist(),
                "image_size": list(self.image_size or (0, 0)),
                "captured_at": _now_iso(),
            }
        if self.R_robot_camera is not None and self.t_robot_camera is not None:
            payload["extrinsics"] = {
                "R_robot_camera": self.R_robot_camera.flatten().tolist(),
                "t_robot_camera_mm": self.t_robot_camera.flatten().tolist(),
                "captured_at": _now_iso(),
            }
        with open(target, "w") as f:
            json5.dump(payload, f, indent=2)
        return target
