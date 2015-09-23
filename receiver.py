#!/usr/bin/python
"""
Lightweight Audio Communication
"""

import socket
import pyaudio
from os import system
from collections import deque
from sys import argv

# Chunk size = 512
# Can't send more than 1472 bytes through a socket
CHUNK = 512
# Audio track format = 16bit signed int
AUDIO_FORM = pyaudio.paInt16
# Audio sample width
AUDIO_SAMP_WIDTH = 2
# Number of channels = 1
AUDIO_CHAN = 1
# Audio sampling rate = 8000 Hz
AUDIO_RATE = 8000

# Communication partner has to be set somewhere
partner_ip = "111.1.111.1"
# Partner's port
partner_port = 17001

# Initialize PyAudio
p = pyaudio.PyAudio()

received = deque()

# Sending socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Receiving socket
sr = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def rec_callback(in_data, frame_count, time_info, status):
    global sr
    sr.sendto(in_data, (partner_ip, partner_port))

    return (None, pyaudio.paContinue)
    #return (None, pyaudio.paComplete)

def play_callback(in_data, frame_count, time_info, status):
    global received
    if len(received) != 0:
        return (received.popleft(), pyaudio.paContinue)
    else:
        return (bytes(1024*2), pyaudio.paContinue)

    #return (None, pyaudio.paComplete)

# Initialize PyAudio Stream
AUDIO_PLAY_STREAM = p.open(
    format=AUDIO_FORM,
    channels=AUDIO_CHAN,
    rate=AUDIO_RATE,
    input=False, output=True,
    frames_per_buffer=CHUNK,
    stream_callback=play_callback)

AUDIO_REC_STREAM = p.open(
    format=AUDIO_FORM,
    channels=AUDIO_CHAN,
    rate=AUDIO_RATE,
    input=True, output=False,
    frames_per_buffer=CHUNK,
    stream_callback=rec_callback)



def forward_port(int_port, ext_port, time):
    """
    Forward a port using miniupnp
    """

    command = "upnpc -a %r %r %r UDP %r" % (
        socket.gethostbyname(socket.gethostname()),
        int_port, ext_port, time
        )
    system(command)

def receive(port, r_only):
    """
    Receive speach bytes
    """

    global s

   
    
    AUDIO_REC_STREAM.start_stream()
    AUDIO_PLAY_STREAM.start_stream()

    if r_only:
        AUDIO_REC_STREAM.close()

    communicate = True
    while communicate:
        data, addr = s.recvfrom(CHUNK*AUDIO_SAMP_WIDTH)
        received.append(data)
        print(214)

    if not r_only:
        AUDIO_REC_STREAM.close()

    AUDIO_PLAY_STREAM.close()

def print_info():
    print("Usage:")
    print("./receiver.py in_port ext_port partner_export partner_ip receive_only")
    print("Example:")
    print("./receiver.py 17001 17002 17003 1.2.3.4 0")

if len(argv) < 5:
    print_info()
    exit(1)
else:
    partner_port = int(argv[3])
    partner_ip = argv[4]

    host = socket.gethostbyname(socket.gethostname())
    port = int(argv[1])

    s.bind((host, port))



forward_port(argv[1], argv[2], 300)
r_only = False
if len(argv) > 5:
    r_only = argv[5] == "1"
receive(int(argv[1]), r_only)
s.close()
sr.close()
p.terminate()
