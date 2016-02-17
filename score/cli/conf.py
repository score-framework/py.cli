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

import os
import sys
import re
from score.init import parse_config_file as parse
from collections import OrderedDict
import textwrap


def venv_root(venv=None):
    if venv is not None:
        return venv
    if hasattr(sys, 'real_prefix'):
        return sys.prefix
    if hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix:
        return sys.prefix
    return None


def confroot(*, global_=False, venv=None):
    if global_:
        if venv is not None:
            raise ValueError('Parameters *global_* and *venv* are mutually '
                             'exclusive')
        root = os.getenv('HOME') or os.getenv('HOMEPATH')
    else:
        root = venv_root(venv)
        if not root:
            root = os.getenv('HOME') or os.getenv('HOMEPATH')
    return os.path.join(root, '.score')


def addconf(name, path, *, venv=None):
    assert re.match(r'^[a-zA-Z0-9_-]+$', name)
    assert not name.startswith('__')
    root = confroot(venv=venv)
    root = os.path.join(root, 'conf')
    os.makedirs(root, exist_ok=True)
    file = os.path.join(root, name)
    open(file, 'w').write(textwrap.dedent('''
        [score.init]
        based_on =
            %s
            %s
        ''' % (defaultconf(global_=True), path)))


def delconf(name, *, venv=None):
    file = os.path.join(confroot(venv=venv), 'conf', name)
    try:
        os.unlink(file)
    except FileNotFoundError:
        pass


def setdefault(name, *, venv=None):
    root = confroot(venv=venv)
    file = os.path.join(root, 'conf', name)
    if not os.path.exists(file):
        raise FileNotFoundError(file)
    open(defaultconf(venv=venv), 'w').write(textwrap.dedent('''
        [score.init]
        based_on =
            %s
            ${here}/%s
    ''' % (globalconf(), name)).strip())


def getdefault(*, venv=None):
    try:
        return os.path.basename(get_origin(defaultconf(venv=venv)))
    except FileNotFoundError:
        return None


def getconf(name, *, venv=None):
    return listconf(venv=venv)[name]


def listconf(*, include_global=True, venv=None):
    files = {}
    if include_global:
        folder = os.getenv('HOME') or os.getenv('HOMEPATH')
        folder = os.path.join(folder, '.score', 'conf')
        try:
            for file in os.listdir(folder):
                files[file] = os.path.join(folder, file)
        except FileNotFoundError:
            pass
    folder = venv_root(venv)
    if folder:
        folder = os.path.join(folder, '.score', 'conf')
        try:
            for file in os.listdir(folder):
                files[file] = os.path.join(folder, file)
        except FileNotFoundError:
            pass
    sortedfiles = OrderedDict()
    for name in sorted(files):
        if name.startswith('__'):
            continue
        sortedfiles[name] = files[name]
    return sortedfiles


def get_origin(file):
    parsedconf = parse(file, recurse=False)
    base = parsedconf['score.init']['based_on']
    if '\n' in base:
        base = base.split('\n')[-1]
    return base


def globalconf():
    file = os.path.join(confroot(global_=True), 'conf', '__global__')
    os.makedirs(os.path.dirname(file), exist_ok=True)
    try:
        open(file, 'x').write(textwrap.dedent('''
            # This is the global CLI configuration file for your SCORE
            # installation. The values defined here will be available in
            # *all* your command line applications.
        ''').strip())
    except FileExistsError:
        pass
    return file


def defaultconf(*, global_=False, venv=None):
    file = os.path.join(confroot(global_=global_, venv=venv),
                        'conf', '__default__')
    os.makedirs(os.path.dirname(file), exist_ok=True)
    try:
        open(file, 'x').write(textwrap.dedent('''
            [score.init]
            based_on = %s
        ''' % globalconf()).strip())
    except FileExistsError:
        pass
    return file
