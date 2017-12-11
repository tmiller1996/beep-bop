import threading
import numpy as np
import sounddevice as sd


class Microphone(threading.Thread):
    def __init__(self, device = None, block_duration = 50, error_callback = None):
        super().__init__(daemon=True)
        self.device = device
        self.samplerate = sd.query_devices(device, 'input')['default_samplerate']
        self.blocksize = int(self.samplerate * block_duration / 1000)
        self.channels = 1
        self.callbacks = []
        self.error_callback = error_callback

    def add_callback(self, callback):
        self.callbacks.append(callback)

    def run(self):
        # sounddevice callback
        def sd_callback(data, frame, time, status):
            if status:
                if self.error_callback is not None:
                    self.error_callback(status)
            if any(data):
                volume = np.max(np.abs(data))
                pitch = None # TODO get pitch from data
                for callback in self.callbacks:
                    callback(volume, pitch)
        with sd.InputStream(device = self.device, channels = self.channels, callback = sd_callback,
                            blocksize = self.blocksize, samplerate = self.samplerate):
            while True:
                pass