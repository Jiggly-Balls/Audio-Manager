from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

device = AudioUtilities.GetSpeakers()
interface = device.Acticate(IAudioEndpointVolume._iid_)
