import sys

from PySide6 import QtWidgets
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QSlider,
    QGroupBox,
    QFormLayout,
    QPushButton,
)
from PySide6.QtCore import Qt

from config import FONT, OPACITY_LEVEL, TITLE_NAME, WINDOW_HEIGHT, WINDOW_WIDTH


class MainWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.scroll_area = QtWidgets.QScrollArea(parent=self)
        self.scroll_area.setGeometry(
            0, 0, self.width() - 200, self.height() + 100
        )
        self.scroll_area.setWidgetResizable(True)
        # self.scroll_area.setFixedHeight(600)
        # self.scroll_area.setMax

        form_layout = QFormLayout()
        group_box = QGroupBox("Testing")

        labels = []
        buttons = []

        for i in range(30):
            labels.append(QLabel(f"Label {i}"))
            # buttons.append(QPushButton(f"Label {i}"))
            label, slider = self.create_slider()
            buttons.append(slider)
            form_layout.addRow(labels[i], buttons[i])
            form_layout.addRow(label)

        group_box.setLayout(form_layout)
        self.scroll_area.setWidget(group_box)

        # self.createSlider()

    def create_slider(self) -> tuple[QSlider, QLabel]:
        # hbox = QHBoxLayout()
        # hbox2 = QHBoxLayout()

        slider = QSlider(parent=self.scroll_area)
        slider.setOrientation(Qt.Orientation.Horizontal)
        slider.setFixedWidth(250)
        slider.setTickPosition(QSlider.TickPosition.TicksAbove)
        slider.setTickInterval(250)
        slider.setMinimum(0)
        slider.setMaximum(1000)
        # slider.setGeometry(WINDOW_WIDTH // 3, WINDOW_HEIGHT // 2, 250, 50)
        # slider.resize(100, 150)

        label = QLabel("0.0%", parent=self.scroll_area)
        label.setFont(FONT)
        label.setGeometry(WINDOW_WIDTH // 1.7, WINDOW_HEIGHT // 3, 250, 70)

        def changedValue() -> None:
            size = slider.value()
            label.setText(f"{size / 10}%")

        slider.valueChanged.connect(changedValue)

        # hbox.addWidget(self.slider)
        # hbox2.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)

        # setLayout(hbox)
        # setLayout(hbox2)
        # label.show()
        # slider.show()
        return slider, label


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MainWidget()
    widget.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    widget.setWindowTitle(TITLE_NAME)
    widget.setWindowOpacity(OPACITY_LEVEL)
    widget.show()

    sys.exit(app.exec())
