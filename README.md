HuePlayer
=========

A very (very) simple mp3 (and others, look inside) player that uses the Philips
Hue lights as a nice visualization engine.

Does not require anything but python 2.7

Built using:

- BASS Sound Library: http://www.un4seen.com/bass.html
- Maxim Kolosov's pybass bindings (tweaked by Eliuk Blau): http://sourceforge.net/projects/pybass/
- phue Philips Hue HTTP JSON API wrapper by Nathanaël Lécaudé: https://github.com/studioimaginaire/phue


## Usage

``$ python hueplayer.py filename [-l|--lights lights] [-u|--username username] [-i|--ip address] [--register] [--microphone]``


*Note: If this is the first time you're using your bridge (or you don't
know/have an username), look all the way down to the --register option.*


Where:

- ``filename``: Filename or path to the file to be played.
- ``-l|--lights``: Number of lights to animate, the lights will respond in ascending order (1 - lower frequencies, N - higher frequencies).
- ``-u|--username``: Username to be presented when comunicating with the bridge.
- ``-i|--ip``: IP address of the bridge to connect to.
- ``--register``: Perform an username registration, the username argument must be supplied also. Be sure to press the bridge button before doing this. Usernames must contain 10 characters at minimum.
- ``--microphone``: Use the system microphone input instead of a file, ignores the filename parameter.


The player cannot be paused and can be stopped with Ctrl+C only. Yes, is that simple.