from __future__ import annotations

import threading
import time
import psutil

from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
from pycaw.pycaw import (
    AudioUtilities,
    IAudioEndpointVolume,
    ISimpleAudioVolume,
)
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
    QScrollArea,
    QWidget,
    QLabel,
    QGroupBox,
    QFormLayout,
)
from typing import final, TYPE_CHECKING

from core.config import (
    EVENT_REGISTRY_SLEEP,
    FONT,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from core.events import MasterVolumeEvent, SessionVolumeEvent
from core.helpers import OpenedApps, ClosedApps, truncate_float, VolumeSlider


if TYPE_CHECKING:
    from typing import Any


@final
class AppWidget(QWidget):
    speak = Signal((OpenedApps,), (ClosedApps,))  # pyright:ignore[reportArgumentType]

    def __init__(self) -> None:
        super().__init__()

        self.speak[OpenedApps].connect(self.app_session_event)  # pyright:ignore[reportIndexIssue, reportUnknownMemberType]
        self.speak[ClosedApps].connect(self.app_session_event)  # pyright:ignore[reportIndexIssue, reportUnknownMemberType]

        self.running = True
        self.scroll_area: QScrollArea = QScrollArea(parent=self)
        self.scroll_area.setGeometry(
            0,
            0,
            WINDOW_WIDTH,
            WINDOW_HEIGHT,
        )
        self.scroll_area.setWidgetResizable(True)

        self.form_layout: QFormLayout = QFormLayout()
        self.slider_map: dict[str, tuple[VolumeSlider, QLabel]] = {}
        group_box = QGroupBox("Volume Controller")

        self.create_master_slider()

        all_sessions: list[Any] = AudioUtilities.GetAllSessions()

        for session in all_sessions:
            volume = session._ctl.QueryInterface(ISimpleAudioVolume)

            if session.Process:
                name = session.Process.name()
                process_label = QLabel(name)
                slider, percentage_label = self.create_session_slider(volume)
                self.slider_map[name] = (slider, process_label)

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

    @Slot(OpenedApps)
    @Slot(ClosedApps)  # pyright:ignore[reportArgumentType]
    def app_session_event(self, apps_data: OpenedApps | ClosedApps) -> None:
        if isinstance(apps_data, OpenedApps):
            for app in apps_data.apps:
                if app not in self.slider_map:
                    session = apps_data.session_map[app]
                    volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                    slider, percentage_label = self.create_session_slider(
                        volume
                    )

                    process_label = QLabel(app)

                    self.form_layout.addRow(process_label, percentage_label)
                    self.form_layout.addRow(slider)

                    session_callback = SessionVolumeEvent(
                        session_volume_slider=slider
                    )
                    session.register_notification(session_callback)

                    self.slider_map[app] = (slider, process_label)

        elif isinstance(apps_data, ClosedApps):
            for app in apps_data.apps:
                if app in self.slider_map:
                    for w in self.slider_map[app]:
                        self.form_layout.removeRow(w)
                    del self.slider_map[app]

    def app_session_registry(self) -> None:
        while self.running:
            all_sessions: list[Any] = AudioUtilities.GetAllSessions()
            current_apps: set[str] = set()
            current_session_map: dict[str, Any] = {}

            for session in all_sessions:
                if session.Process:
                    try:
                        app_name = session.Process.name()
                    except psutil.NoSuchProcess:
                        continue

                    current_apps.add(app_name)
                    current_session_map[app_name] = session

            old_apps = set(self.slider_map.keys())
            new_apps = current_apps - (old_apps & current_apps)
            closed_apps = old_apps - (old_apps & current_apps)

            if closed_apps:
                self.speak[ClosedApps].emit(ClosedApps(apps=closed_apps))  # pyright:ignore[reportIndexIssue, reportUnknownMemberType]

            if new_apps:
                self.speak[OpenedApps].emit(  # pyright:ignore[reportIndexIssue, reportUnknownMemberType]
                    OpenedApps(
                        apps=new_apps,
                        session_map=current_session_map,
                    )
                )

            time.sleep(EVENT_REGISTRY_SLEEP)

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
        percentage_label = QLabel(
            f"{master_volume}%",
        )
        percentage_label.setFont(FONT)

        slider = VolumeSlider()
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

        self.form_layout.addRow(process_label, percentage_label)
        self.form_layout.addRow(slider)

    def create_session_slider(
        self, volume_controller: Any
    ) -> tuple[VolumeSlider, QLabel]:
        app_volume = volume_controller.GetMasterVolume()
        app_volume = truncate_float(app_volume * 100)

        label = QLabel(f"{app_volume}%")
        label.setFont(FONT)

        slider = VolumeSlider()
        slider.setSliderPosition(int(app_volume * 10))

        def changedValue() -> None:
            changed_volume = slider.value()
            volume_controller.SetMasterVolume(changed_volume / 1000, None)
            label.setText(f"{changed_volume / 10}%")

        slider.valueChanged.connect(changedValue)

        return slider, label
