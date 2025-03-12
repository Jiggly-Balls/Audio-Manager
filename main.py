import sys

from PySide6.QtWidgets import QApplication

from core.app import AppWidget
from core.config import (
    OPACITY_LEVEL,
    TITLE_NAME,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)


if __name__ == "__main__":
    app = QApplication([])

    widget = AppWidget()
    widget.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    widget.setWindowTitle(TITLE_NAME)
    widget.setWindowOpacity(OPACITY_LEVEL)
    widget.show()

    sys.exit(app.exec())
