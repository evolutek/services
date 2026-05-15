"""UVC (V4L2) camera driver with built-in ArUco detection and ChArUco calibration.

Ported from evo_lib.drivers.camera.uvc, stripped for the legacy services stack:
  - Task[()] return types collapsed to plain functions (synchronous, raise on error)
  - evo_lib.logger.Logger replaced by stdlib logging.Logger (compatible API)
  - evo_lib.peripheral.Placable parent replaced by ABC (only ``name`` is kept)
  - DriverDefinition / ArgTypes wiring dropped — instantiate the class directly
  - REPL command bindings (commands.register, Camera ABC methods like
    get_marker_ids/get_markers_robot/get_markers_table) dropped — they live
    in the cellaserv service layer (evolutek.services.camera)
"""

from __future__ import annotations

import logging
import os
import subprocess
import threading
import time
from abc import ABC
from typing import TYPE_CHECKING, Any

from evolutek.lib.vision.aruco import ArucoState, CharucoCalibrationSession
from evolutek.lib.vision.markers import (
    DEFAULT_ARUCO_DICTIONARY,
    DEFAULT_CHARUCO_MARKER_MM,
    DEFAULT_CHARUCO_SQUARE_MM,
    DEFAULT_CHARUCO_SQUARES_X,
    DEFAULT_CHARUCO_SQUARES_Y,
    ArucoMarker,
)

if TYPE_CHECKING:
    import numpy as np


DEFAULT_FOURCC = "MJPG"
DEFAULT_WIDTH = 1920
DEFAULT_HEIGHT = 1080
DEFAULT_READER_FPS = 200


def _v4l2_set_ctrl(device: str, ctrl: str, value: int) -> tuple[bool, str]:
    result = subprocess.run(
        ["v4l2-ctl", "-d", device, f"--set-ctrl={ctrl}={value}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.returncode == 0, (result.stderr or "").strip()


def _v4l2_has_ctrl(device: str, ctrl: str) -> bool:
    result = subprocess.run(
        ["v4l2-ctl", "-d", device, "--list-ctrls"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and ctrl in result.stdout


class _AbstractUvcCamera(ABC):
    """Shared layer for UVC camera drivers; subclasses provide the V4L2 ops."""

    def __init__(
        self,
        name: str,
        logger: logging.Logger,
        device: str,
        width: int = DEFAULT_WIDTH,
        height: int = DEFAULT_HEIGHT,
        fourcc: str = DEFAULT_FOURCC,
        focus: "int | None" = None,
        autofocus: bool = False,
        settings: "dict[str, int] | None" = None,
        marker_size_mm: float = 32.0,
        dictionary: str = DEFAULT_ARUCO_DICTIONARY,
        calibration_path: "str | None" = None,
        charuco_squares_x: int = DEFAULT_CHARUCO_SQUARES_X,
        charuco_squares_y: int = DEFAULT_CHARUCO_SQUARES_Y,
        charuco_square_mm: float = DEFAULT_CHARUCO_SQUARE_MM,
        charuco_marker_mm: float = DEFAULT_CHARUCO_MARKER_MM,
        reader_fps: int = DEFAULT_READER_FPS,
        tag_sizes_mm: "dict[int, float] | None" = None,
    ):
        self.name = name
        self._log = logger
        self._device = device
        self._width = width
        self._height = height
        self._fourcc = fourcc
        self._focus = focus
        self._autofocus = autofocus
        self._settings = dict(settings) if settings else {}
        self._reader_fps = reader_fps
        self._aruco = ArucoState(
            marker_size_mm=marker_size_mm,
            dictionary=dictionary,
            charuco_squares_x=charuco_squares_x,
            charuco_squares_y=charuco_squares_y,
            charuco_square_mm=charuco_square_mm,
            charuco_marker_mm=charuco_marker_mm,
            calibration_path=calibration_path,
            tag_sizes_mm=tag_sizes_mm,
        )
        self._init_state()

    def set_tag_sizes_mm(self, tag_sizes_mm: "dict[int, float]") -> None:
        """Inject a per-id marker size table (e.g. Eurobot tag set). Application-level."""
        self._aruco.tag_sizes_mm.update(tag_sizes_mm)

    def _init_state(self) -> None:
        """Hook for subclasses to initialize their private V4L2/replay state."""

    def init(self) -> None:
        raise NotImplementedError

    def close(self) -> None:
        raise NotImplementedError

    def capture(self) -> "np.ndarray":
        raise NotImplementedError

    def set_focus(self, value: int) -> None:
        raise NotImplementedError

    def set_setting(self, name: str, value: int) -> None:
        raise NotImplementedError

    def detect(self) -> list[ArucoMarker]:
        return self._aruco.detect_in_frame(self.capture())

    def calibration_session(self) -> CharucoCalibrationSession:
        return self._aruco.calibration_session()

    def apply_intrinsics(self, intrinsics: dict[str, Any]) -> None:
        self._aruco.apply_intrinsics(intrinsics)

    def calibrate_extrinsics(
        self,
        reference_marker_id: int,
        R_robot_marker: "np.ndarray",
        t_robot_marker_mm: "np.ndarray",
    ) -> dict[str, Any]:
        return self._aruco.calibrate_extrinsics(
            self.detect(), reference_marker_id, R_robot_marker, t_robot_marker_mm
        )

    def is_intrinsics_loaded(self) -> bool:
        return self._aruco.is_intrinsics_loaded()

    def is_extrinsics_loaded(self) -> bool:
        return self._aruco.is_extrinsics_loaded()

    def save_calibration(self, path: "str | None" = None) -> None:
        self._aruco.save(path)

    @property
    def K(self) -> "np.ndarray | None":
        return self._aruco.K

    @property
    def dist(self) -> "np.ndarray | None":
        return self._aruco.dist

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height


class UvcCamera(_AbstractUvcCamera):
    def _init_state(self) -> None:
        self._cap = None
        self._lock = threading.Lock()
        # Background reader: drops stale buffers so capture() always returns fresh.
        self._read_thread: "threading.Thread | None" = None
        self._read_stop = threading.Event()
        self._latest_frame: "np.ndarray | None" = None
        self._latest_frame_lock = threading.Lock()

    def init(self) -> None:
        import cv2

        # AF must be locked before VideoCapture grabs its first buffer,
        # otherwise focal length floats and any K calibrated downstream is invalid.
        if _v4l2_has_ctrl(self._device, "focus_automatic_continuous"):
            af_value = 1 if self._autofocus else 0
            ok, err = _v4l2_set_ctrl(self._device, "focus_automatic_continuous", af_value)
            if not ok:
                self._log.warning(
                    f"UvcCamera '{self.name}': could not set focus_automatic_continuous "
                    f"on {self._device}: {err}"
                )
        elif self._autofocus:
            self._log.warning(
                f"UvcCamera '{self.name}': autofocus requested but {self._device} "
                f"has no focus_automatic_continuous control (fixed-focus lens)"
            )
        if self._focus is not None and not self._autofocus:
            _v4l2_set_ctrl(self._device, "focus_absolute", self._focus)

        for ctrl, value in self._settings.items():
            ok, err = _v4l2_set_ctrl(self._device, ctrl, value)
            if not ok:
                self._log.warning(
                    f"UvcCamera '{self.name}': v4l2 ctrl {ctrl}={value} ignored ({err})"
                )

        self._cap = cv2.VideoCapture(self._device, cv2.CAP_V4L2)
        if not self._cap.isOpened():
            raise RuntimeError(f"UvcCamera '{self.name}': failed to open {self._device}")

        # FOURCC before size: UVC's resolution table is format-dependent.
        self._cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*self._fourcc))
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)
        self._cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        self._width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self._height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        loaded = self._aruco.load()
        self._log.info(
            f"UvcCamera '{self.name}' opened on {self._device} "
            f"@ {self._width}x{self._height} {self._fourcc} "
            f"(focus={'AUTO' if self._autofocus else self._focus}, "
            f"calibration={'loaded' if loaded else 'absent'})"
        )
        self._read_stop.clear()
        # Non-daemon: close() is responsible for stopping the thread cleanly.
        self._read_thread = threading.Thread(
            target=self._read_loop,
            name=f"uvc-read-{self.name}",
            daemon=False,
        )
        self._read_thread.start()

    def _read_loop(self) -> None:
        idle_backoff_s = 1.0 / max(self._reader_fps, 1)
        while not self._read_stop.is_set():
            with self._lock:
                cap = self._cap
            if cap is None:
                break
            try:
                ok, frame = cap.read()
            except Exception:
                break
            if ok and frame is not None:
                with self._latest_frame_lock:
                    self._latest_frame = frame
            else:
                time.sleep(idle_backoff_s)

    def close(self) -> None:
        self._read_stop.set()
        if self._read_thread is not None:
            self._read_thread.join(timeout=1.0)
            self._read_thread = None
        with self._lock:
            if self._cap is not None:
                self._cap.release()
                self._cap = None
        with self._latest_frame_lock:
            self._latest_frame = None
        self._log.info(f"UvcCamera '{self.name}' closed")

    def capture(self) -> "np.ndarray":
        if self._cap is None:
            raise RuntimeError(f"UvcCamera '{self.name}' not opened")
        deadline = time.monotonic() + 1.0
        while True:
            with self._latest_frame_lock:
                frame = self._latest_frame
            if frame is not None:
                return frame
            if time.monotonic() > deadline:
                raise RuntimeError(f"UvcCamera '{self.name}': no frame available")
            time.sleep(0.005)

    def set_focus(self, value: int) -> None:
        ok, err = _v4l2_set_ctrl(self._device, "focus_absolute", value)
        if not ok:
            self._log.warning(f"UvcCamera '{self.name}': set_focus({value}) failed: {err}")
        else:
            self._focus = value

    def set_setting(self, name: str, value: int) -> None:
        ok, err = _v4l2_set_ctrl(self._device, name, value)
        if not ok:
            self._log.warning(f"UvcCamera '{self.name}': set_setting({name}) failed: {err}")
        else:
            self._settings[name] = value

    def save_calibration(self, path: "str | None" = None) -> None:
        target = self._aruco.save(path)
        self._log.info(f"UvcCamera '{self.name}' saved calibration -> {target}")
