#!/usr/bin/env python3
import math
import numpy as np
import shutil
import argparse

def int_or_str(text):
    """Helper function for arg parsing"""
    try:
        return int(text)
    except ValueError:
        return text

parser = argparse.ArgumentParser(description="Description goes here")
parser.add_argument('-l', '--list-devices', action='store_true', help='List audio devices')
parser.add_argument('-b', '--block-duration', type=float, metavar='DURATION', default=50, help='block size (default %(default)s milliseconds)')
parser.add_argument('-d', '--device', type=int_or_str, help='input device (numeric ID or substring)')
parser.add_argument('-g', '--gain', type=float, default=10, help='initial gain factor (default %(default)s)')
parser.add_argument('-r', '--range', type=float, nargs=2, metavar=('LOW', 'HIGH'), default=[100, 2000])
args = parser.parse_args()

low, high = args.range
if high <= low:
    parser.error('HIGH must be greater than LOW')

try:
    import sounddevice as sd

    if args.list_devices:
        print(sd.query_devices())
        parser.exit(0)

    samplerate = sd.query_devices(args.device, 'input')['default_samplerate']

    # sounddevice callback
    def callback(indata, frame, time, status):
        if status:
            print('status:', str(status))
        if any(indata):
            magnitude = np.abs(np.fft.rfft(indata[:, 0], n=100))
            magnitude *= args.gain / 100
            print('magnitude:', magnitude)
        else:
            print('no input')

    with sd.InputStream(device=args.device, channels=1, callback=callback, blocksize=int(samplerate * args.block_duration / 1000), samplerate=samplerate):
        while True:
            pass
except KeyboardInterrupt:
    parser.exit('interrupted by user')
except Exception as e:
    parser.exit(type(e).__name__ + ": " + str(e))


devices = sd.query_devices()
