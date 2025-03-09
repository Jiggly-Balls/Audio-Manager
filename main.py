import sys

from PySide6 import QtWidgets, QtGui
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSlider
from PySide6.QtCore import Qt

from config import FONT, OPACITY_LEVEL, TITLE_NAME, WINDOW_HEIGHT, WINDOW_WIDTH


class MyWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.createSlider()

    def createSlider(self) -> None:
        # hbox = QHBoxLayout()
        # hbox2 = QHBoxLayout()

        self.slider = QSlider(parent=self)
        self.slider.setOrientation(Qt.Orientation.Horizontal)
        self.slider.setTickPosition(QSlider.TickPosition.TicksAbove)
        self.slider.setTickInterval(10)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setGeometry(WINDOW_WIDTH // 3, WINDOW_HEIGHT // 2, 250, 70)
        # self.slider.resize(100, 150)

        self.slider.valueChanged.connect(self.changedValue)

        self.label = QLabel("0", parent=self)
        self.label.setFont(FONT)
        self.label.setGeometry(WINDOW_WIDTH // 3, WINDOW_HEIGHT // 3, 250, 70)

        # hbox.addWidget(self.slider)
        # hbox2.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)

        # self.setLayout(hbox)
        # self.setLayout(hbox2)
        self.label.show()
        self.slider.show()

    def changedValue(self) -> None:
        size = self.slider.value()
        self.label.setText(str(size))


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
    widget.setWindowTitle(TITLE_NAME)
    widget.setWindowOpacity(OPACITY_LEVEL)
    widget.show()

    sys.exit(app.exec())
