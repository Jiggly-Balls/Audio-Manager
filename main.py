from __future__ import annotations

import sys

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import (
    AudioUtilities,
    IAudioEndpointVolume,
    ISimpleAudioVolume,
)
from PySide6 import QtWidgets
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QSlider,
    QGroupBox,
    QFormLayout,
)
from typing import TYPE_CHECKING

from core.config import FONT, OPACITY_LEVEL, TITLE_NAME, WINDOW_HEIGHT, WINDOW_WIDTH
from core.helpers import truncate_float, VolumeSlider


if TYPE_CHECKING:
    from typing import Any


class MainWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.scroll_area = QtWidgets.QScrollArea(parent=self)
        self.scroll_area.setGeometry(
            0,
            0,
            WINDOW_WIDTH,
            WINDOW_HEIGHT,
        )
        self.scroll_area.setWidgetResizable(True)

        self.labels = []
        self.sliders = []
        self.form_layout = QFormLayout()
        group_box = QGroupBox("Volume Controller")

        self.create_master_slider()

        all_sessions = AudioUtilities.GetAllSessions()

        for session in all_sessions:
            volume = session._ctl.QueryInterface(ISimpleAudioVolume)
            volume.SetMasterVolume(1.0, None)

            if session.Process:
                process_label = QLabel(session.Process.name())
                slider, percentage_label = self.create_session_slider(volume)

                self.labels.append(process_label)
                self.sliders.append(slider)
                self.form_layout.addRow(process_label, percentage_label)
                self.form_layout.addRow(slider)

        group_box.setLayout(self.form_layout)
        self.scroll_area.setWidget(group_box)

    def create_master_slider(self) -> None:
        device = AudioUtilities.GetSpeakers()
        interface = device.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None
        )
        master_volume_controller = cast(
            interface, POINTER(IAudioEndpointVolume)
        )
        master_volume = master_volume_controller.GetMasterVolumeLevelScalar()
        master_volume = truncate_float(master_volume * 100)

        process_label = QLabel("MASTER VOLUME")
        percentage_label = QLabel(f"{master_volume}%", parent=self.scroll_area)
        percentage_label.setFont(FONT)

        slider = VolumeSlider(parent=self.scroll_area)
        slider.setSliderPosition(master_volume * 10)

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
    ) -> tuple[QSlider, QLabel]:
        app_volume = volume_controller.GetMasterVolume()
        app_volume = truncate_float(app_volume * 100)

        label = QLabel(f"{app_volume}%", parent=self.scroll_area)
        label.setFont(FONT)

        slider = VolumeSlider(parent=self.scroll_area)
        slider.setSliderPosition(app_volume * 10)

        def changedValue() -> None:
            changed_volume = slider.value()
            volume_controller.SetMasterVolume(changed_volume / 1000, None)
            label.setText(f"{changed_volume / 10}%")

        slider.valueChanged.connect(changedValue)

        return slider, label


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MainWidget()
    widget.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    widget.setWindowTitle(TITLE_NAME)
    widget.setWindowOpacity(OPACITY_LEVEL)
    widget.show()

    sys.exit(app.exec())
