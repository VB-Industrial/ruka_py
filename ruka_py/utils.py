"""Utilities which do not require a running ROS node."""

from pathlib import Path

import numpy as np
import pandas as pd

PathLike = str | Path


def read_csv(filename: PathLike) -> pd.DataFrame:
    """Read a comma-separated trajectory file.

    Unlike the old script, this function does not hide file and parsing errors.
    The caller therefore gets a useful exception with the bad filename or row.
    """

    return pd.read_csv(filename, sep=",")


def euler_deg_to_quaternion(
    roll_deg: float, pitch_deg: float, yaw_deg: float
) -> np.ndarray:
    """Convert Euler angles in degrees to an ``[x, y, z, w]`` quaternion."""

    roll, pitch, yaw = np.radians([roll_deg, pitch_deg, yaw_deg])

    cy = np.cos(yaw * 0.5)
    sy = np.sin(yaw * 0.5)
    cp = np.cos(pitch * 0.5)
    sp = np.sin(pitch * 0.5)
    cr = np.cos(roll * 0.5)
    sr = np.sin(roll * 0.5)

    return np.array(
        [
            sr * cp * cy - cr * sp * sy,
            cr * sp * cy + sr * cp * sy,
            cr * cp * sy - sr * sp * cy,
            cr * cp * cy + sr * sp * sy,
        ],
        dtype=float,
    )
