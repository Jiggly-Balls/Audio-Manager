import sys

from PySide6.QtWidgets import QApplication

from core.app import AppWidget
from core.config import (
    OPACITY_LEVEL,
    TITLE_NAME,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)


__version__ = "1.0.0"
__title__ = "Audio-Manager"
__author__ = "Jiggly Balls"
__license__ = "MIT License"
__copyright__ = "Copyright 2024-present Jiggly Balls"


if __name__ == "__main__":
    app = QApplication([])

    widget = AppWidget()
    widget.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    widget.setWindowTitle(TITLE_NAME)
    widget.setWindowOpacity(OPACITY_LEVEL)
    widget.show()

    exit_code = app.exec()
    widget.running = False
    sys.exit(exit_code)
