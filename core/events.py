from __future__ import annotations

from comtypes import COMObject
from pycaw.callbacks import AudioSessionEvents
from pycaw.pycaw import IAudioEndpointVolumeCallback
from typing import TYPE_CHECKING
from typing_extensions import override

from core.helpers import truncate_float

if TYPE_CHECKING:
    from comtypes import IUnknown
    from typing import Any, Literal, ClassVar
    from core.helpers import VolumeSlider


class InstanceVolumeEvent(AudioSessionEvents):
    @override
    def on_simple_volume_changed(
        self, new_volume: float, new_mute: int, event_context: Any
    ) -> None:
        print(
            ":: OnSimpleVolumeChanged callback\n"
            f"new_volume: {new_volume}; "
            f"new_mute: {new_mute}; "
            f"event_context: {event_context.contents}\n"
        )

    @override
    def on_state_changed(
        self,
        new_state: Literal["Inactive", "Active", "Expired"],
        new_state_id: Literal[0, 1, 2],
    ) -> None:
        print(
            ":: OnStateChanged callback\n"
            f"new_state: {new_state}; id: {new_state_id}\n"
        )


class MasterVolumeEvent(COMObject):
    _com_interfaces_: ClassVar[list[type[IUnknown]]] = [
        IAudioEndpointVolumeCallback
    ]

    def __init__(
        self, *args: Any, master_volume_slider: VolumeSlider, **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self.master_volume_slider = master_volume_slider

    def OnNotify(self, p_notify: Any) -> None:
        # print(dir(pNotify))
        self.master_volume_slider.setSliderPosition(
            truncate_float(p_notify.contents.fMasterVolume, 4) * 1000
        )
        # print(dir(p_notify.contents))
        print(f"MASTER VOL: {p_notify.contents.fMasterVolume}")
        print(f"MUTED: {p_notify.contents.bMuted}\n")
