#!/usr/bin/python
#coding:utf-8
"""
HuePlayer: a very simple implementation of an mp3 (and the other types BASS
supports by default) player with the Philips Hue Bulbs feedback.

(c) 2014 - Moisés Cachay Tello

This source is published with no commercial pruposes whatsoever, including
its intended uses, and can be modified as long as the original copyright
notice is preserved. Every other copyrights belongs to their respective owners.
"""

from phue import Bridge
from pybass import *

import argparse
import time


class PlayerBackend(object):
    """
    Player backend abstraction, it makes possible to deliberately plug anything
    that complies with the interface to the player.

    Specifically, this backend uses the C BASS library to operate, it supports
    mp3 and other file formats without codecs, and it's very small (~200kb).
    Also I'm using a bindings file from Maxim Kolosov with a little fixes made
    by Eliuk Blau.

    See more about BASS in: http://www.un4seen.com/bass.html
    BASS bindings homepage: http://sourceforge.net/projects/pybass/
    """

    @staticmethod
    def init():
        """Backend initialization procedures."""
        # Start bass in the default output device.
        # The Player doesnt use this method's return value (TODO?).
        return BASS_Init(-1, 44100, 0, 0, 0)

    @staticmethod
    def get_stream(file):
        """Stream instance generator."""
        # In this case, BASS returns a handle for this file stream.
        return BASS_StreamCreateFile(False, bytes(file), 0, 0, 0)

    @staticmethod
    def play_stream(stream, callback=None, sleep_time=.1, lights=None):
        """Plays the generated stream, triggering the callback periodically."""
        # We let BASS play the stream while we work.
        BASS_ChannelPlay(stream, False)

        # This piece of code was cruelly ported from the BASS source example
        # called livespec, which made exactly what I wanted. I'm still
        # wondering how it works...
        while True:
            y, y1, b0 = 0., 0, 0
            fft = (ctypes.c_float*1024)()
            BASS_ChannelGetData(stream, fft, BASS_DATA_FFT2048)
            band_list = []
            for band in range(lights):
                peak = 0
                b1 = 2 ** band*10./(lights-1)
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
            if callback:
                callback(band_list)
            time.sleep(sleep_time)


class HuePlayer(object):
    """
    Player abstraction. Initializes the Hue bridge comunication and lights, uses
    a given backend to play a stream and implements the callback function that
    changes the bulbs states.
    """

    ip = '10.12.50.197'
    username = 'mcachay000'
    lights = 4
    backend_class = PlayerBackend
    sleep_time = .1

    def __init__(self, args, backend_class=None):
        """
        Instance constructor. Receives the object that argparse returns to set
        it's values and an optional backend class to use.
        """

        self.bridge = None
        self.file = args.file
        self.ip = args.ip
        self.username = args.username
        self.lights = args.lights
        if backend_class:
            self.backend_class = backend_class

    def play(self):
        """
        'Main' play routine, initializes everything and starts playing.
        """
        self.backend_class.init()
        self.bridge_init()
        stream = self.backend_class.get_stream(self.file)
        self.lights_init()
        self.backend_class.play_stream(stream, self.hue_callback,
                                       sleep_time=self.sleep_time,
                                       lights=self.lights)

    def bridge_init(self):
        """
        Bridge communication initialization.
        """
        self.bridge = Bridge(ip=self.ip, username=self.username)

    def lights_init(self):
        """
        Pre-play lights initialization.
        """

        # Actually does nothing (transitiontime is set per-request)
        for i in range(self.lights):
            self.bridge.set_light(i+1, 'transitiontime', 0)

    def hue_callback(self, band_list):
        """
        Callback for each 'frame' captured by the stream (with a previously set
        period). The only argument is a list with the N values (N = number of
        lights) corresponding a Nth band value in the range 0-100.

        Example: For 3 lights, band_list would come with [30, 54, 100], meaning
        that, in this frame the 'bass' band is weaker than the 'high' band.

        This implementation changes hue and saturation equally in direct
        relation to the band levels.
        """

        for band in range(len(band_list)):
            self.bridge.set_light(
                band+1,
                {
                    'bri': band_list[band],
                    'hue': 65530/100 * band_list[band],
                    'sat': 255/100 * band_list[band],
                    'transitiontime': 4
                }
            )


class MicBackend(PlayerBackend):
    """
    A player backend that uses the system microphone instead of reading a file.
    """

    @staticmethod
    def init():
        return BASS_RecordInit(-1)

    @staticmethod
    def get_stream(file):
        return BASS_RecordStart(44100, 1, 0, MicBackend.recording, 0)

    @staticmethod
    @RECORDPROC
    def recording(handle, buffer, length, user):
        """
        Recording callback required by BASS_RecordStart to perform any needed 
        transformation to the record stream.
        """
        return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?', help='file to play')
    parser.add_argument('-l', '--lights', default=4, type=int, required=False,
                        help='number of lights')
    parser.add_argument('-u', '--username', default=HuePlayer.username,
                        help='API username')
    parser.add_argument('-i', '--ip', default=HuePlayer.ip,
                        help='IP address of bridge')
    parser.add_argument('--register', action='store_true',
                        help='register with API')
    parser.add_argument('--microphone', action='store_true',
                        help='use microphone instead of playing a file')
    args = parser.parse_args()

    # Why did I put this here? There was no other place to put it without
    # messing too much with the code.
    if args.register:
        if not args.username:
            print 'You must supply an username to register with the API'
        try:
            bridge = Bridge(ip=args.ip, username=args.username)
            bridge.connect()
            print 'Everything went well, use your username to play from now on'
        except:
            print 'Could not register with API, maybe you didn\'t pressed ' \
                  'the button in the last 30 seconds'
        sys.exit(0)

    # One can just simply register, without supplying a filename.
    elif args.microphone:
        HuePlayer(args, backend_class=MicBackend).play()
    elif not args.file:
        print 'You must supply filename to play'
        sys.exit(0)

    HuePlayer(args).play()