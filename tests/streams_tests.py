import math
import os
import unittest

import numpy

from consyn import streams
from consyn import models
from consyn import commands

from . import SOUND_DIR
from . import DummySession


class FrameSampleReaderTest(unittest.TestCase):

    def test_iterframes_in_order(self):
        path = os.path.join(SOUND_DIR, "amen-stereo.wav")

        result = [streams.Pool(initial={"path": path})] \
            >> streams.AubioFrameLoader(bufsize=1024, hopsize=1024) \
            >> list

        self.assertEqual(len(result), 138)

        previous = 0
        for pool in result:
            frame = pool["frame"]
            self.assertTrue(previous <= frame.index)
            self.assertEqual(frame.samplerate, 44100)
            previous = frame.index

        self.assertEqual(previous, 68)


class OnsetSlicerTest(unittest.TestCase):

    def _onset_test(self, path, channels, expected_onsets, expected_duration):
        path = os.path.join(SOUND_DIR, path)

        result = [streams.Pool(initial={"path": path})] \
            >> streams.AubioFrameLoader(bufsize=1024, hopsize=1024) \
            >> streams.OnsetSlicer(
                winsize=1024,
                threshold=0,
                min_slice_size=0,
                method="default") \
            >> list

        self.assertEqual(len(result) / channels, expected_onsets)

        for i in range(channels):
            pos = -(i + 1)
            self.assertEqual(
                expected_duration,
                result[pos]["frame"].position + result[pos]["frame"].duration)

    def test_simple_stereo_segments(self):
        self._onset_test("amen-stereo.wav", 2, 10, 70560)

    def test_simple_mono_segments(self):
        self._onset_test("amen-mono.wav", 1, 10, 70560)


class SampleAnalyserTest(unittest.TestCase):

    def test_same_buffersize(self):
        bufsize = 1024
        duration = 70560
        channels = 2
        path = os.path.join(SOUND_DIR, "amen-stereo.wav")

        analyser = streams.SampleAnalyser(winsize=bufsize, hopsize=bufsize)

        result = [streams.Pool(initial={"path": path})] \
            >> streams.AubioFrameLoader(bufsize=bufsize, hopsize=bufsize) \
            >> analyser \
            >> list

        self.assertEqual(math.ceil(duration * channels / float(bufsize)),
                         len(result))

        for res in result:
            for method in analyser.methods:
                self.assertIsInstance(res["features"][method], numpy.float32)

    def test_different_sizes(self):
        bufsize = 1024
        path = os.path.join(SOUND_DIR, "amen-stereo.wav")

        analyser = streams.SampleAnalyser(winsize=1024, hopsize=512)

        result = [streams.Pool(initial={"path": path})] \
            >> streams.AubioFrameLoader(bufsize=bufsize, hopsize=bufsize) \
            >> streams.OnsetSlicer(
                winsize=1024,
                threshold=0,
                min_slice_size=0,
                method="default") \
            >> analyser \
            >> list

        self.assertEqual(len(result), 20)

        for res in result:
            for method in analyser.methods:
                self.assertIsInstance(res["features"][method], numpy.float32)


class UnitSampleReaderTests(unittest.TestCase):

    def test_read_whole_file(self):
        bufsize = 1024
        path = os.path.join(SOUND_DIR, "amen-stereo.wav")
        unit = models.Unit(channel=0, position=0, duration=70560)

        self.assertEqual(unit.duration, 70560)
        self.assertEqual(unit.channel, 0)
        self.assertEqual(unit.position, 0)

        initial = [streams.Pool(initial={"path": path, "unit": unit})]
        loader = streams.AubioUnitLoader(bufsize=bufsize, hopsize=bufsize)
        result = initial >> loader >> list

        self.assertEqual(len(result), 1)
        samples = result[0]["frame"].samples

        self.assertEqual(samples.shape, (70560,))
        self.assertNotEqual(numpy.sum(samples), 0)

    def test_multiple_reads(self):
        reads = 10
        bufsize = 1024
        path = os.path.join(SOUND_DIR, "amen-stereo.wav")
        unit = models.Unit(channel=0, position=0, duration=70560)

        self.assertEqual(unit.duration, 70560)
        self.assertEqual(unit.channel, 0)
        self.assertEqual(unit.position, 0)

        loader = streams.AubioUnitLoader(bufsize=bufsize, hopsize=bufsize)

        for index in range(reads):
            initial = [streams.Pool(initial={"path": path, "unit": unit})]
            result = initial >> loader >> list

            self.assertEqual(len(result), 1)
            samples = result[0]["frame"].samples

            self.assertEqual(samples.shape, (70560,))
            self.assertNotEqual(numpy.sum(samples), 0)

        self.assertEqual(index, reads - 1)


class UnitGeneratorTests(unittest.TestCase):

    def _test_iter_amount(self, name, num):
        session = DummySession()
        path = os.path.join(SOUND_DIR, name)
        corpus = commands.add_corpus(session, path)
        initial = [streams.Pool(initial={"corpus": corpus})]
        results = initial >> streams.UnitGenerator(session) >> list
        self.assertEqual(len(results), num)

    def test_stereo(self):
        self._test_iter_amount("amen-stereo.wav", 20)

    def test_mono(self):
        self._test_iter_amount("amen-mono.wav", 10)


class DurationClipperTests(unittest.TestCase):

    def _test_simple(self, samples, unit_dur, unit_pos, target_dur,
                     target_pos):
        target = models.Unit(duration=target_dur, position=target_pos)
        unit = models.Unit(duration=unit_dur, position=unit_pos)

        pool = streams.Pool(initial={
            "frame": streams.AudioFrame(samples=samples),
            "target": target,
            "unit": unit
        })

        results = [pool] >> streams.DurationClipper() >> list

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["samples"].shape[0], target_dur)

    def test_less_than(self):
        self._test_simple(numpy.arange(18), 18, 3, 20, 2)

    def test_more_than(self):
        self._test_simple(numpy.arange(25), 25, 3, 20, 2)

    def test_equal(self):
        self._test_simple(numpy.arange(20), 20, 2, 20, 2)