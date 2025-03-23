from __future__ import annotations

from typing import TYPE_CHECKING

import pystray
from PIL import Image, ImageDraw
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
from pystray import Menu, MenuItem

from core.config import TITLE_NAME

if TYPE_CHECKING:
    from pystray._win32 import Icon


def create_image(width: int, height: int, color1: str, color2: str) -> None:
    # Generate an image and draw a pattern
    image = Image.new("RGB", (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle((width // 2, 0, width, height // 2), fill=color2)
    dc.rectangle((0, height // 2, width // 2, height), fill=color2)

    return image


class IconTray:
    def __init__(self, image_path: None | str = None) -> None:
        self.icon = pystray.Icon(
            TITLE_NAME,
            icon=image_path or create_image(64, 64, "black", "white"),
            menu=Menu(
                MenuItem("Mute All", self.mute_all_callback),
                MenuItem("Unmute All", self.unmute_all_callback),
            ),
        )

    def mute_all_callback(self, icon: Icon, item: MenuItem) -> None:
        all_sessions = AudioUtilities.GetAllSessions()
        for session in all_sessions:
            volume = session._ctl.QueryInterface(ISimpleAudioVolume)
            if session.Process:
                volume.SetMute(1, None)

    def unmute_all_callback(self, icon: Icon, item: MenuItem) -> None:
        all_sessions = AudioUtilities.GetAllSessions()
        for session in all_sessions:
            volume = session._ctl.QueryInterface(ISimpleAudioVolume)
            if session.Process:
                volume.SetMute(0, None)

    def run(self) -> None:
        self.icon.run_detached()

    def stop(self) -> None:
        self.icon.stop()
