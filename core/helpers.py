from __future__ import annotations

import time

from dataclasses import dataclass
from pycaw.pycaw import (
    AudioUtilities,
    ISimpleAudioVolume,
)
from PySide6.QtWidgets import QSlider, QLabel
from PySide6.QtCore import Qt, QThread
from typing import TYPE_CHECKING

from core.events import SessionVolumeEvent
from core.config import FONT

if TYPE_CHECKING:
    from typing import Any
    from core.app import AppWidget


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


class AppSessionRegistry(QThread):
    def __init__(
        self, app_widget: AppWidget, *args: Any, **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self.app_widget = app_widget

    def run(self) -> None:
        while self.app_widget.running:
            # print("CHECK\n")
            all_sessions: list[Any] = AudioUtilities.GetAllSessions()
            current_apps: set[str] = set()
            current_session_map: dict[str, Any] = {}

            for session in all_sessions:
                # volume.SetMasterVolume(1.0, None)

                if session.Process:
                    # volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                    app_name = session.Process.name()
                    current_apps.add(app_name)
                    current_session_map[app_name] = session
                    if app_name not in self.app_widget.slider_map:
                        print(f"NEW APP: {app_name}")

            old_apps = set(self.app_widget.slider_map.keys())
            new_apps = current_apps - (old_apps & current_apps)
            closed_apps = old_apps - (old_apps & current_apps)

            for app in closed_apps:
                for w in self.app_widget.slider_map[app]:
                    self.app_widget.form_layout.removeRow(w)
                del self.app_widget.slider_map[app]
                print(f"REMOVED {app}")

            for app in new_apps:
                session = current_session_map[app]
                volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                # slider, percentage_label = self.create_session_slider(volume)

                app_volume = volume.GetMasterVolume()
                app_volume = truncate_float(app_volume * 100)

                percentage_label = QLabel(f"{app_volume}%")
                percentage_label.setFont(FONT)

                slider = VolumeSlider()
                slider.setSliderPosition(int(app_volume * 10))

                def changedValue() -> None:
                    changed_volume = slider.value()
                    volume.SetMasterVolume(changed_volume / 1000, None)
                    percentage_label.setText(f"{changed_volume / 10}%")

                slider.valueChanged.connect(changedValue)

                #################

                process_label = QLabel(app)

                self.app_widget.form_layout.addRow(
                    process_label, percentage_label
                )
                self.app_widget.form_layout.addRow(slider)

                session_callback = SessionVolumeEvent(
                    session_volume_slider=slider
                )
                session.register_notification(session_callback)

                self.app_widget.slider_map[app] = (slider, process_label)

                print(f"ADDED: {app}")

            print(f"\nOPENED: {new_apps}")
            print(f"CLOSED: {closed_apps}")
            time.sleep(1)
