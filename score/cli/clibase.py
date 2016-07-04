# Copyright © 2015,2016 STRG.AT GmbH, Vienna, Austria
#
# This file is part of the The SCORE Framework.
#
# The SCORE Framework and all its parts are free software: you can redistribute
# them and/or modify them under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation which is in the
# file named COPYING.LESSER.txt.
#
# The SCORE Framework and all its parts are distributed without any WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. For more details see the GNU Lesser General Public
# License.
#
# If you have not received a copy of the GNU Lesser General Public License see
# http://www.gnu.org/licenses/.
#
# The License-Agreement realised between you as Licensee and STRG.AT GmbH as
# Licenser including the issue of its valid conclusion and its pre- and
# post-contractual effects is governed by the laws of Austria. Any disputes
# concerning this License-Agreement including the issue of its valid conclusion
# and its pre- and post-contractual effects are exclusively decided by the
# competent court, in whose district STRG.AT GmbH has its registered seat, at
# the discretion of STRG.AT GmbH also the competent court, in whose district the
# Licensee has his registered seat, an establishment or assets.

import click
from pkg_resources import iter_entry_points
from .conf import default_file, get_file
from score.init import init_from_file, parse_config_file
import logging
import os


class ScoreCLI(click.MultiCommand):
    """
    Master command loading sub-commands from plugins.
    """

    def list_commands(self, ctx):
        result = []
        for entrypoint in iter_entry_points(group='score.cli'):
            result.append(entrypoint.name)
        result.sort()
        return result

    def get_command(self, ctx, name):
        plugins = list(iter_entry_points(group='score.cli', name=name))
        if len(plugins) == 0:
            message = 'Entry point "%s" not found' % name
            raise click.ClickException(message)
        elif len(plugins) > 1:
            message = 'Entry point "%s" found in multiple packages:' % name
            for plugin in plugins:
                message += '\n - %s' % plugin.dist
            raise click.ClickException(message)
        return plugins[0].load()


class Configuration:

    def __init__(self, path):
        self.given_path = path
        self._conf = None

    @property
    def path(self):
        if self.given_path is not None:
            return self.given_path
        return default_file()

    def parse(self):
        return parse_config_file(self.path)

    def load(self, module=None):
        if self._conf is None:
            self._conf = init_from_file(self.path)
        if module is None:
            return self._conf
        return getattr(self._conf, module)


@click.command(cls=ScoreCLI)
@click.option('-c', '--conf', 'conf', help='The configuration to use.')
@click.pass_context
def main(ctx, conf=None):
    if conf and not os.path.isfile(conf):
        conf = get_file(conf)
    logger = logging.getLogger()
    ctx.obj = {
        'conf': Configuration(conf),
        'log': logger,
    }


if __name__ == '__main__':
    main()
