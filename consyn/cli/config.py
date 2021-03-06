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
import sys

import click

from . import configurator
from .. import settings


@click.option("--defaults", is_flag=True, default=False,
              help="Show default settings.")
@click.command("config", short_help="Update configuration.")
@configurator
def command(config, defaults):
    if defaults:
        click.echo(settings.DEFAULT_CONFIG)
        sys.exit(0)

    with open(settings.CONFIG_PATH, "r") as fp:
        result = click.edit(fp.read())

    if result is not None:
        with open(settings.CONFIG_PATH, "w") as fp:
            fp.write(result)
