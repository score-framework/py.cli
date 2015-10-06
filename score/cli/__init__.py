# Copyright © 2015 STRG.AT GmbH, Vienna, Austria
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
from .config import config
from pkg_resources import iter_entry_points
import textwrap


class PluginCommand(click.MultiCommand):
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

    def format_help_text(self, ctx, formatter):
        formatter.write_paragraph()
        formatter.write_text(textwrap.indent(textwrap.dedent('''
            Master command loading sub-commands from plugins.
        '''), '  '))
        formatter.write_paragraph()
        formatter.write_text(textwrap.indent(textwrap.dedent('''
            You can use the following in your packages setup.py to register a sub-command called `mysub':
        '''), '  '))
        formatter.write(textwrap.indent(textwrap.dedent('''
            entry_points={
              'score.cli': [
                'mysub = pythonpath.to.main.func:main',
              ]
            }
        '''), '      '))


main = PluginCommand()

if __name__ == '__main__':
    main()

