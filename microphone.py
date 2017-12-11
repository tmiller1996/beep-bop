#!/usr/bin/env python3
import threading
import numpy as np
import sounddevice as sd
import argparse


class Microphone(threading.Thread):
    """A listening device"""

    def __init__(self, device = None, block_duration = 50, error_callback = None):
        """Create a new Microphone object"""
        super().__init__(daemon=True)
        self.device = device
        self.samplerate = sd.query_devices(device, 'input')['default_samplerate']
        self.blocksize = int(self.samplerate * block_duration / 1000)
        self.channels = 1
        self.callbacks = []
        self.error_callback = error_callback

    def add_callback(self, callback):
        """Add a callback to the microphone"""
        self.callbacks.append(callback)

    def run(self):
        """Run the Microphone thread"""
        def sd_callback(data, frame, time, status):
            if status:
                if self.error_callback is not None:
                    self.error_callback(status)
            if any(data):
                volume = np.max(np.abs(data)) # this is a very rough approximation of volume, there's not really a unit or anything
                pitch = None # TODO get pitch from data
                for callback in self.callbacks:
                    callback(volume, pitch)
        with sd.InputStream(device = self.device, channels = self.channels, callback = sd_callback,
                            blocksize = self.blocksize, samplerate = self.samplerate):
            while True:
                pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-l', '--list-devices',
                        action='store_true', help='show list of audio devices and exit')
    args = parser.parse_args()
    if args.list_devices:
        if any(sd.query_devices()):
            print(sd.query_devices())
        else:
            print('None listeds')
        parser.exit(0)
    else:
        print('nothing to do')
