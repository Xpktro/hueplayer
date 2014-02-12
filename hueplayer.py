#coding:utf-8

import time
import ctypes
from pybass import *


BASS_Init(-1, 44100, 0, 0, 0)

handle_ = BASS_StreamCreateFile(False, b'hiddenplace.mp3', 0, 0, 0)
BASS_ChannelPlay(handle_, False)

while True:

    y, y1, b0 = 0., 0, 0
    fft = (ctypes.c_float*1024)()
    BASS_ChannelGetData(handle_, fft, BASS_DATA_FFT2048)
    bands = 3
    band_list = []
    for band in range(bands):
        peak = 0
        b1 = 2 ** band*10./(bands-1)
        if b1 > 1023:
            b1 = 1023
        if b1 <= b0:
            b1 = b0 + 1
        while b0 < b1:
            if peak < fft[1+b0]:
                peak = fft[1+b0]
            b0 += 1
        y = (peak ** .5) * 3 * 100
        if y > 100:
            y = 100
        band_list.append(int(y))
    print band_list

    time.sleep(.1)
