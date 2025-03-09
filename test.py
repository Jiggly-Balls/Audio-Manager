from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import (
    AudioUtilities,
    IAudioEndpointVolume,
    ISimpleAudioVolume,
)

device = AudioUtilities.GetSpeakers()
interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# volume.SetMasterVolumeLevel(0, None)  # Range: [-65.0, 0.0]
# volume.SetMasterVolumeLevelScalar(0.5, None)  # Range: [0.0, 1.0]
# current = volume.GetMasterVolumeLevelScalar()
# print(current)

all_sessions = AudioUtilities.GetAllSessions()
for session in all_sessions:
    volume = session._ctl.QueryInterface(ISimpleAudioVolume)
    volume.SetMasterVolume(1.0, None)

    if session.Process:
        print(session.Process.name())
