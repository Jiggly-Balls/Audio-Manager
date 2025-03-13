from __future__ import annotations

import threading
import time

from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
from pycaw.pycaw import (
    AudioUtilities,
    IAudioEndpointVolume,
    ISimpleAudioVolume,
)
from PySide6.QtWidgets import (
    QScrollArea,
    QWidget,
    QLabel,
    QGroupBox,
    QFormLayout,
)
from typing import TYPE_CHECKING

from core.config import (
    FONT,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from core.events import MasterVolumeEvent, SessionVolumeEvent
from core.helpers import truncate_float, VolumeSlider


if TYPE_CHECKING:
    from typing import Any


class AppWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.running = True
        self.scroll_area: QScrollArea = QScrollArea(parent=self)
        self.scroll_area.setGeometry(
            0,
            0,
            WINDOW_WIDTH,
            WINDOW_HEIGHT,
        )
        self.scroll_area.setWidgetResizable(True)

        self.labels: list[QLabel] = []
        self.sliders: list[VolumeSlider] = []
        self.form_layout: QFormLayout = QFormLayout()
        self.slider_map: dict[str, VolumeSlider] = {}
        group_box = QGroupBox("Volume Controller")

        self.create_master_slider()

        all_sessions: list[Any] = AudioUtilities.GetAllSessions()

        for session in all_sessions:
            volume = session._ctl.QueryInterface(ISimpleAudioVolume)
            # volume.SetMasterVolume(1.0, None)

            if session.Process:
                name = session.Process.name()
                process_label = QLabel(name)
                slider, percentage_label = self.create_session_slider(volume)
                self.slider_map[name] = slider

                self.labels.append(process_label)
                self.sliders.append(slider)
                self.form_layout.addRow(process_label, percentage_label)
                self.form_layout.addRow(slider)

                session_callback = SessionVolumeEvent(
                    session_volume_slider=slider
                )
                session.register_notification(session_callback)

        group_box.setLayout(self.form_layout)
        self.scroll_area.setWidget(group_box)

        self.app_session_registry_thread = threading.Thread(
            target=self.app_session_registry
        )
        self.app_session_registry_thread.start()

    def app_session_registry(self) -> None:
        while self.running:
            # print("CHECK\n")
            all_sessions: list[Any] = AudioUtilities.GetAllSessions()
            current_apps: set[str] = set()

            for session in all_sessions:
                volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                # volume.SetMasterVolume(1.0, None)

                if session.Process:
                    app_name = session.Process.name()
                    current_apps.add(app_name)
                    if app_name not in self.slider_map:
                        print(f"NEW APP: {app_name}")

            old_apps = set(self.slider_map.keys())
            new_apps = current_apps - (old_apps & current_apps)
            closed_apps = old_apps - (old_apps & current_apps)

            print(f"\nOPENED: {new_apps}")
            print(f"CLOSED: {closed_apps}")
            time.sleep(1)

    def create_master_slider(self) -> None:
        device: Any = AudioUtilities.GetSpeakers()
        interface: Any = device.Activate(
            IAudioEndpointVolume._iid_,  # pyright:ignore[reportPrivateUsage]
            CLSCTX_ALL,
            None,
        )
        master_volume_controller: Any = cast(
            interface, POINTER(IAudioEndpointVolume)
        )
        master_volume = master_volume_controller.GetMasterVolumeLevelScalar()
        master_volume = truncate_float(master_volume * 100)

        process_label = QLabel("MASTER VOLUME")
        percentage_label = QLabel(f"{master_volume}%", parent=self.scroll_area)
        percentage_label.setFont(FONT)

        slider = VolumeSlider(parent=self.scroll_area)
        slider.setSliderPosition(int(master_volume * 10))

        master_callback = MasterVolumeEvent(master_volume_slider=slider)
        master_volume_interface = interface.QueryInterface(
            IAudioEndpointVolume
        )
        master_volume_interface.RegisterControlChangeNotify(master_callback)

        def changedValue() -> None:
            changed_volume = slider.value()
            master_volume_controller.SetMasterVolumeLevelScalar(
                changed_volume / 1000, None
            )
            percentage_label.setText(f"{changed_volume / 10}%")

        slider.valueChanged.connect(changedValue)

        self.labels.append(process_label)
        self.sliders.append(slider)
        self.form_layout.addRow(process_label, percentage_label)
        self.form_layout.addRow(slider)

    def create_session_slider(
        self, volume_controller: Any
    ) -> tuple[VolumeSlider, QLabel]:
        app_volume = volume_controller.GetMasterVolume()
        app_volume = truncate_float(app_volume * 100)

        label = QLabel(f"{app_volume}%", parent=self.scroll_area)
        label.setFont(FONT)

        slider = VolumeSlider(parent=self.scroll_area)
        slider.setSliderPosition(int(app_volume * 10))

        def changedValue() -> None:
            changed_volume = slider.value()
            volume_controller.SetMasterVolume(changed_volume / 1000, None)
            label.setText(f"{changed_volume / 10}%")

        slider.valueChanged.connect(changedValue)

        return slider, label
