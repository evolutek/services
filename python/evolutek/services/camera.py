#!/usr/bin/env python3
"""Camera service: UVC + ArUco detection, exposed over cellaserv.

Architecture:
  - Wraps evolutek.lib.vision.UvcCamera (ported from evo_lib).
  - Background thread runs detection at ``detect_period_ms`` and publishes
    detected markers as the ``camera_markers`` cellaserv event.
  - Synchronous actions for one-shot snapshots, focus tweaking, extrinsics
    recalibration against a fixed Eurobot table tag, and pose-from-tag.
  - Calibration files (intrinsics + extrinsics) live as a JSON5 produced
    by the standalone calibrate-camera CLI; this service only consumes them.

Config (cellaserv [camera] section):
    device              : V4L2 path (e.g. /dev/CAM_FACE1)
    width, height       : capture resolution (defaults 1280x720)
    fourcc              : FOURCC tag (default MJPG)
    focus               : fixed-focus value (int) or omit for auto
    dictionary          : ArUco dict name (default DICT_4X4_100)
    calibration_path    : JSON5 with {intrinsics, extrinsics}
    detect_period_ms    : detection cadence (default 100 = 10 Hz)
    publish_markers     : true/false, publish detections (default true)
    use_eurobot_tags    : true/false, load Eurobot per-id sizes (default true)
"""

import atexit
import math
import os
import threading
import time
from typing import Any

from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service
from cellaserv.settings import make_logger

from evolutek.lib.settings import ROBOT
from evolutek.lib.vision import (
    EUROBOT_FIXED_TABLE_TAGS,
    EUROBOT_TAG_SIZES_MM,
    ArucoMarker,
    UvcCamera,
)


def _marker_to_dict(m: ArucoMarker) -> "dict[str, Any]":
    """Serialize an ArucoMarker for cellaserv transport (numpy → list)."""
    out: "dict[str, Any]" = {"id": int(m.id)}
    if m.position_robot_mm is not None:
        out["x_mm"] = float(m.position_robot_mm[0])
        out["y_mm"] = float(m.position_robot_mm[1])
        out["z_mm"] = float(m.position_robot_mm[2])
    if m.quat_robot is not None:
        qw, qx, qy, qz = m.quat_robot
        out["qw"] = qw
        out["qx"] = qx
        out["qy"] = qy
        out["qz"] = qz
    if m.yaw_robot_rad is not None:
        out["yaw_rad"] = float(m.yaw_robot_rad)
    return out


def _yaw_from_robot_to_table(
    rx_mm: float, ry_mm: float, ryaw_rad: float,
    mx_mm: float, my_mm: float, myaw_rad: float,
) -> "tuple[float, float, float]":
    """Deduce robot pose in table frame from one observed fixed tag.

    Inputs:
      (rx, ry, ryaw) : tag pose in robot frame (observed by camera)
      (mx, my, myaw) : tag pose in table frame (Eurobot known constant)
    Returns: (robot_x_mm, robot_y_mm, robot_yaw_rad) in table frame.

    T_table_robot = T_table_marker . T_marker_robot
    T_marker_robot = inverse(T_robot_marker)
    Yaw-only 2D compose (cos/sin precomputed once — keeps the math cheap).
    """
    # Inverse of T_robot_marker (2D rigid-body)
    cy, sy = math.cos(ryaw_rad), math.sin(ryaw_rad)
    inv_x = -(rx_mm * cy + ry_mm * sy)
    inv_y = -(-rx_mm * sy + ry_mm * cy)
    inv_yaw = -ryaw_rad

    # Compose T_table_marker . T_marker_robot
    cm, sm = math.cos(myaw_rad), math.sin(myaw_rad)
    out_x = mx_mm + inv_x * cm - inv_y * sm
    out_y = my_mm + inv_x * sm + inv_y * cm
    out_yaw = myaw_rad + inv_yaw
    return out_x, out_y, out_yaw


@Service.require("config")
class Camera(Service):

    def __init__(self):
        super().__init__(ROBOT)
        self.cs = CellaservProxy()
        self.log = make_logger("camera")
        self.is_initialized = False
        self._cam: "UvcCamera | None" = None
        self._loop_stop = threading.Event()
        self._loop_thread: "threading.Thread | None" = None
        self._last_markers: list[ArucoMarker] = []
        self._last_markers_lock = threading.Lock()
        atexit.register(self.stop)

        cfg = self._load_config()
        if cfg is None:
            return  # is_initialized stays False; main() will bail

        try:
            self._cam = UvcCamera(
                name=f"camera-{ROBOT}",
                logger=self.log,
                device=cfg["device"],
                width=cfg["width"],
                height=cfg["height"],
                fourcc=cfg["fourcc"],
                focus=cfg["focus"],
                autofocus=cfg["autofocus"],
                dictionary=cfg["dictionary"],
                calibration_path=cfg["calibration_path"],
                tag_sizes_mm=EUROBOT_TAG_SIZES_MM if cfg["use_eurobot_tags"] else None,
            )
            self._cam.init()
        except Exception as e:
            self.log.error("[CAMERA] Failed to init UvcCamera: %s", e)
            return

        self._detect_period_s = cfg["detect_period_ms"] / 1000.0
        self._publish_markers = cfg["publish_markers"]
        self._loop_thread = threading.Thread(
            target=self._detect_loop, name="camera-detect", daemon=True
        )
        self._loop_thread.start()
        self.is_initialized = True
        self.log.info(
            "[CAMERA] ready (device=%s, %dx%d, dict=%s, period=%dms, publish=%s)",
            cfg["device"], cfg["width"], cfg["height"], cfg["dictionary"],
            cfg["detect_period_ms"], cfg["publish_markers"],
        )

    def _load_config(self) -> "dict[str, Any] | None":
        try:
            section = self.cs.config.get_section("camera")
        except Exception as e:
            self.log.error("[CAMERA] No [camera] section in cellaserv config: %s", e)
            return None

        def _get(key, default=None, cast=str):
            raw = section.get(key, default)
            if raw is None or raw == "":
                return default
            try:
                return cast(raw)
            except Exception:
                return default

        device = section.get("device", "").strip()
        if not device:
            self.log.error("[CAMERA] config.camera.device is required")
            return None

        return {
            "device": device,
            "width": _get("width", 1280, int),
            "height": _get("height", 720, int),
            "fourcc": _get("fourcc", "MJPG", str),
            "focus": _get("focus", None, int),
            "autofocus": str(_get("autofocus", "false", str)).lower() in ("1", "true", "yes"),
            "dictionary": _get("dictionary", "DICT_4X4_100", str),
            "calibration_path": _get("calibration_path", None, str),
            "detect_period_ms": _get("detect_period_ms", 100, int),
            "publish_markers": str(_get("publish_markers", "true", str)).lower() in ("1", "true", "yes"),
            "use_eurobot_tags": str(_get("use_eurobot_tags", "true", str)).lower() in ("1", "true", "yes"),
        }

    def _detect_loop(self) -> None:
        while not self._loop_stop.is_set():
            t0 = time.monotonic()
            try:
                markers = self._cam.detect() if self._cam else []
            except Exception as e:
                self.log.warning("[CAMERA] detect() failed: %s", e)
                markers = []
            with self._last_markers_lock:
                self._last_markers = markers
            if self._publish_markers and markers:
                self.publish("camera_markers", markers=[_marker_to_dict(m) for m in markers])
            elapsed = time.monotonic() - t0
            sleep_s = self._detect_period_s - elapsed
            if sleep_s > 0:
                self._loop_stop.wait(sleep_s)

    def stop(self) -> None:
        if self._loop_stop.is_set():
            return
        self._loop_stop.set()
        if self._loop_thread is not None:
            self._loop_thread.join(timeout=1.0)
        if self._cam is not None:
            try:
                self._cam.close()
            except Exception as e:
                self.log.warning("[CAMERA] close() failed: %s", e)
        self.log.info("[CAMERA] stopped")

    # ---------------- Cellaserv actions ----------------

    @Service.action
    def snapshot(self) -> "list[dict[str, Any]]":
        """One-shot synchronous detect, returns markers in robot frame."""
        if self._cam is None:
            return []
        markers = self._cam.detect()
        with self._last_markers_lock:
            self._last_markers = markers
        return [_marker_to_dict(m) for m in markers]

    @Service.action
    def last_markers(self) -> "list[dict[str, Any]]":
        """Last detection result from the background loop (no fresh capture)."""
        with self._last_markers_lock:
            return [_marker_to_dict(m) for m in self._last_markers]

    @Service.action
    def is_intrinsics_loaded(self) -> bool:
        return self._cam is not None and self._cam.is_intrinsics_loaded()

    @Service.action
    def is_extrinsics_loaded(self) -> bool:
        return self._cam is not None and self._cam.is_extrinsics_loaded()

    @Service.action
    def set_focus(self, value=0) -> bool:
        if self._cam is None:
            return False
        try:
            self._cam.set_focus(int(value))
            return True
        except Exception as e:
            self.log.warning("[CAMERA] set_focus(%s) failed: %s", value, e)
            return False

    @Service.action
    def get_robot_pose_in_table(self) -> "dict[str, Any]":
        """Deduce the robot pose in the table frame from a visible Eurobot fixed tag.

        Returns {"x_mm", "y_mm", "yaw_rad", "from_tag_id", "ok": bool}.
        Picks the first matching fixed tag in the current frame.
        """
        if self._cam is None or not self._cam.is_extrinsics_loaded():
            return {"ok": False, "reason": "extrinsics not loaded"}
        markers = self._cam.detect()
        for m in markers:
            if m.id in EUROBOT_FIXED_TABLE_TAGS and m.position_robot_mm is not None \
                    and m.yaw_robot_rad is not None:
                mx, my, _mz, myaw = EUROBOT_FIXED_TABLE_TAGS[m.id]
                rx = float(m.position_robot_mm[0])
                ry = float(m.position_robot_mm[1])
                ryaw = float(m.yaw_robot_rad)
                px, py, pyaw = _yaw_from_robot_to_table(rx, ry, ryaw, mx, my, myaw)
                return {
                    "ok": True,
                    "x_mm": px,
                    "y_mm": py,
                    "yaw_rad": pyaw,
                    "from_tag_id": int(m.id),
                }
        return {"ok": False, "reason": "no fixed Eurobot tag visible",
                "visible_ids": [int(m.id) for m in markers]}

    @Service.action
    def recalibrate_extrinsics(self, reference_marker_id=0) -> "dict[str, Any]":
        """Calibrate camera→robot extrinsics from a visible Eurobot fixed tag.

        The reference tag's table-frame pose is assumed (Eurobot known). This
        only makes sense when the robot pose is known beforehand (e.g. parked
        at the calibration mark). Returns the computed extrinsics dict or an
        error message.
        """
        import numpy as np

        if self._cam is None:
            return {"ok": False, "reason": "camera not initialized"}
        ref_id = int(reference_marker_id)
        if ref_id not in EUROBOT_FIXED_TABLE_TAGS:
            return {"ok": False, "reason": f"id {ref_id} is not an Eurobot fixed tag"}

        # Table-frame pose of the reference tag (yaw-only, fixed orientation)
        mx, my, mz, myaw = EUROBOT_FIXED_TABLE_TAGS[ref_id]

        # Build R_robot_marker assuming the robot is at table origin facing +X.
        # Caller should park accordingly. Pure yaw rotation around Z.
        cy, sy = math.cos(myaw), math.sin(myaw)
        R_robot_marker = np.array(
            [[cy, -sy, 0.0], [sy, cy, 0.0], [0.0, 0.0, 1.0]], dtype=np.float64
        )
        t_robot_marker_mm = np.array([mx, my, mz], dtype=np.float64)
        try:
            result = self._cam.calibrate_extrinsics(ref_id, R_robot_marker, t_robot_marker_mm)
            self._cam.save_calibration()
            return {"ok": True, **result}
        except Exception as e:
            self.log.warning("[CAMERA] recalibrate_extrinsics failed: %s", e)
            return {"ok": False, "reason": str(e)}


def main():
    cam = Camera()
    if not cam.is_initialized:
        print("[CAMERA] Failed to initialize service")
        return
    cam.run()


if __name__ == "__main__":
    main()
