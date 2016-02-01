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
from .conf import (
    listconf, addconf, delconf, getconf, getdefault, setdefault, get_origin)
import os
import re
from score.init import parse_config_file as parse


def name_from_file(file):
    return re.sub(r'\..*', '', os.path.basename(file))


@click.group('conf')
def main():
    """
    Manages configurations.
    """
    pass


@main.command('list')
@click.option('-p', '--paths', is_flag=True, default=False)
def conf_list(paths):
    """
    Lists available configurations.
    """
    default = getdefault()
    tpl = '{name} {default}'
    if paths:
        tpl += ' ({path})'
    for conf, path in listconf().items():
        print(tpl.format(
            name=conf,
            default='*' if conf == default else ' ',
            path=get_origin(path),
        ))


@main.command('add')
@click.argument('file')
@click.option('-n', '--name', 'name')
@click.option('-d', '--make-default', 'make_default',
              is_flag=True, default=False)
def conf_add(file, name=None, make_default=False):
    """
    Adds a new configuration.
    """
    file = os.path.abspath(file)
    if name is None:
        name = name_from_file(file)
    addconf(name, file)
    if make_default:
        setdefault(name)


@main.command('setdefault')
@click.argument('name')
def conf_setdefault(name):
    """
    Adds a new configuration.
    """
    setdefault(name)


CONFIRM_DELETE = 'Delete configuration `%s\'?'
CONFIRM_DELETE_WRONG_PATH = \
    'WARNING: Path mismatch!\n' \
    ' Configured file: {real}\n' \
    ' You provided:    {provided})\n'\
    '\n' \
    'Proceed anyway and delete configuration `{name}\'? '


@main.command('del')
@click.argument('name')
@click.option('-f', '--force', 'force', is_flag=True, default=False)
@click.pass_context
def conf_del(clickctx, name, force):
    """
    Deletes a configuration.
    """
    if re.match('^[a-zA-Z0-9_-]+$', name):
        if name == getdefault() and not force:
            raise click.ClickException(
                'Pass --force to delete default configuration')
        if force or click.confirm(CONFIRM_DELETE % name):
            delconf(name)
        return
    # assume *name* is actually the path to a file
    file = name
    file = os.path.realpath(file)
    name = name_from_file(file)
    conf = getconf(name)
    confirmed = False
    try:
        parsedconf = parse(conf, recurse=False)
    except FileNotFoundError:
        pass
    else:
        configured = parsedconf['score.init']['based_on']
        if file != configured:
            msg = CONFIRM_DELETE_WRONG_PATH.format(
                name=name,
                real=configured,
                provided=file,
            )
            if click.confirm(msg):
                confirmed = True
            else:
                return
    if force or (not confirmed and click.confirm(CONFIRM_DELETE % name)):
        delconf(name)


if __name__ == '__main__':
    main()
