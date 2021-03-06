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
import os

from consyn.base import Pipeline
from consyn.commands import add_mediafile
from consyn.utils import UnitGenerator

from . import DatabaseTests
from . import SOUND_DIR


class UnitGeneratorTests(DatabaseTests):

    def _test_iter_amount(self, name, num):
        path = os.path.join(SOUND_DIR, name)
        mediafile = add_mediafile(self.session, path, segmentation="beats")

        pipeline = Pipeline([
            UnitGenerator(mediafile, self.session),
            list
        ])

        results = pipeline.run()
        self.assertEqual(len(results), num)

    def test_stereo(self):
        self._test_iter_amount("amen-stereo.wav", 26)

    def test_mono(self):
        self._test_iter_amount("amen-mono.wav", 13)
