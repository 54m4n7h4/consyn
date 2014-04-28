# -*- coding: utf-8 -*-
import aubio
import numpy

from .base import SliceStream
from .base import AudioFrame
from ..settings import DTYPE


__all__ = [
    "OnsetSlicer"
]


class BaseSlicer(SliceStream):

    def __init__(self, min_slice_size=8192):
        super(BaseSlicer, self).__init__()
        self.min_slice_size = min_slice_size
        self.detectors = {}
        self.buffers = {}
        self.onsets = {}
        self.positions = {}

    def observe(self, frame):
        samples = frame.samples
        read = frame.duration
        position = frame.position
        channel = frame.channel
        samplerate = frame.samplerate
        path = frame.path

        output = None
        self.path = path
        self.samplerate = samplerate

        if channel not in self.detectors:
            self.add_channel(channel)

        self.positions[channel] = position + read
        self.buffers[channel] = numpy.concatenate((self.buffers[channel],
                                                   samples))

        detector = self.detectors[channel]

        if detector(samples):
            position = detector.get_last() * 2
            length = len(self.onsets[channel])
            if length == 0 or (position - self.onsets[channel][0] >
                               self.min_slice_size):
                self.onsets[channel].append(position)
            if len(self.onsets[channel]) == 2:
                output = self.flush(channel)

        return output

    def finish(self):
        for channel in self.onsets:
            self.onsets[channel].append(self.positions[channel])
            yield self.flush(channel)

    def get_detector(self):
        raise NotImplementedError()

    def add_channel(self, channel):
        self.detectors[channel] = self.get_detector()
        self.buffers[channel] = numpy.array([], dtype=DTYPE)
        self.onsets[channel] = []
        self.positions[channel] = 0

    def flush(self, channel):
        duration = self.onsets[channel][1] - self.onsets[channel][0]
        samples = self.buffers[channel][:duration]
        position = self.onsets[channel][0]

        self.buffers[channel] = self.buffers[channel][duration:]
        self.onsets[channel] = [self.onsets[channel][1]]

        frame = AudioFrame()
        frame.samplerate = self.samplerate
        frame.path = self.path
        frame.samples = samples
        frame.channel = channel
        frame.position = position
        frame.duration = duration
        return frame


class OnsetSlicer(BaseSlicer):

    def __init__(self, winsize=1024, threshold=-70, method="default",
                 min_slice_size=8192):
        super(OnsetSlicer, self).__init__(min_slice_size=min_slice_size)
        self.winsize = winsize
        self.hopsize = winsize / 2
        self.threshold = threshold
        self.method = method

    def get_detector(self):
        detector = aubio.onset(self.method, self.winsize, self.hopsize)
        detector.set_threshold(self.threshold)
        return detector