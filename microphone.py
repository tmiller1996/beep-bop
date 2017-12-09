#!/usr/bin/env python3
import threading
import numpy as np
import sounddevice as sd


class Microphone(threading.Thread):
    def __init__(self, delegate, device=None, block_duration = 50):
        super().__init__(daemon=True)
        self.delegate = delegate
        self.device = device
        self.samplerate = sd.query_devices(device, 'input')['default_samplerate']
        self.blocksize = int(self.samplerate * block_duration / 1000)
        self.channels = 1

    def run(self):
        def callback(data, frame, time, status):
            if status:
                self.delegate(str(status))
            if any(data):
                self.delegate(np.max(np.abs(data)))
            else:
                self.delegate('no input')
        with sd.InputStream(device = self.device, channels = self.channels, callback = callback, blocksize = self.blocksize, samplerate = self.samplerate):
            while True:
                pass