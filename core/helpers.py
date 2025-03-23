from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSlider

if TYPE_CHECKING:
    from typing import Any


def truncate_float(d: float, visible: int = 1) -> float:
    d: str = str(d)
    point_index = d.index(".")
    truncated = d[:point_index] + d[point_index : point_index + visible + 1]
    return float(truncated)


@dataclass
class ClosedApps:
    apps: set[str]


@dataclass
class OpenedApps:
    apps: set[str]
    session_map: dict[str, Any]


class VolumeSlider(QSlider):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.setOrientation(Qt.Orientation.Horizontal)
        self.setFixedWidth(250)
        self.setTickInterval(250)
        self.setTickPosition(QSlider.TickPosition.TicksAbove)
        self.setMinimum(0)
        self.setMaximum(1000)
