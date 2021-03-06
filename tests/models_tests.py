# -*- coding: utf-8 -*-
# Copyright (C) 2014, David Poulter
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import unicode_literals
import unittest

from consyn.models import Features
from consyn.models import MediaFile
from consyn.models import Unit
from consyn import settings


class MediaFileTests(unittest.TestCase):

    def test_name(self):
        mediafile = MediaFile(path="/test/case.mp3")
        self.assertEqual(mediafile.name, "case")
        mediafile = MediaFile()
        self.assertEqual(mediafile.name, None)

    def test_repr(self):
        mediafile = MediaFile(id=0, path="/test/case.mp3", duration=10,
                              channels=1, samplerate=80)
        r = "id=0, name=case, duration=10, channels=1, samplerate=80, units=0"
        self.assertEqual(str(mediafile), "<MediaFile({})>".format(r))


class UnitTests(unittest.TestCase):

    def test_repr(self):
        mediafile = MediaFile(id=0, path="/test/case.mp3", duration=10,
                              channels=1, samplerate=80)
        unit = Unit(id=0, channel=1, position=1, duration=20)
        unit.mediafile = mediafile
        r = "mediafile=case, id=0, channel=1, position=1, duration=20"
        self.assertEqual(str(unit), "<Unit({})>".format(r))


class FeaturesTests(unittest.TestCase):

    def test_init_features(self):
        order = ["feat_3", "feat_2", "feat_1"]
        features = Features({
            "feat_1": 0.1,
            "feat_2": 0.2,
            "feat_3": 0.3
        })

        self.assertEqual(features["feat_1"], 0.1)
        self.assertEqual(features["feat_2"], 0.2)
        self.assertEqual(features["feat_3"], 0.3)

        for index, label, value in features:
            self.assertEqual(order[index], label)

        self.assertEqual(
            str(features), "<Features(feat_3=0.3, feat_2=0.2, feat_1=0.1)>")

    def test_to_many_features(self):
        feats = {}
        for index in range(settings.FEATURE_SLOTS + 1):
            feats["test_{}".format(index)] = index
        self.assertRaises(AssertionError, Features, feats)

    def test_get_feature_exception(self):
        features = Features({"feat_1": 0.1})
        self.assertRaises(Exception, features.__getitem__, "feat_2")
