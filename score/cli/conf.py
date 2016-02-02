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


def venv_root():
    if hasattr(sys, 'real_prefix'):
        return sys.prefix
    if hasattr(sys, 'base_prefix') and sys.base_prefix is not sys.prefix:
        return sys.prefix
    return None


def confroot():
    root = venv_root()
    if not root:
        root = os.getenv('HOME') or os.getenv('HOMEPATH')
    return os.path.join(root, '.score')


def addconf(name, path, *, root=None):
    assert re.match(r'^[a-zA-Z0-9_-]+$', name)
    assert not name.startswith('__')
    if root is None:
        root = confroot()
    root = os.path.join(root, 'conf')
    os.makedirs(root, exist_ok=True)
    file = os.path.join(root, name)
    open(file, 'w').write('[score.init]\n'
                          'based_on = %s\n' % path)


def delconf(name):
    file = os.path.join(confroot(), 'conf', name)
    try:
        os.unlink(file)
    except FileNotFoundError:
        pass


def setdefault(name, root=None):
    if root is None:
        root = confroot()
    file = os.path.join(root, 'conf', name)
    if not os.path.exists(file):
        raise FileNotFoundError(file)
    open(_default(), 'w').write('[score.init]\n'
                                'based_on = ${here}/%s\n' % name)


def getdefault():
    try:
        return os.path.basename(get_origin(_default()))
    except FileNotFoundError:
        return None


def getconf(name):
    return listconf()[name]


def listconf():
    files = {}
    folder = os.getenv('HOME') or os.getenv('HOMEPATH')
    folder = os.path.join(folder, '.score', 'conf')
    try:
        for file in os.listdir(folder):
            files[file] = os.path.join(folder, file)
    except FileNotFoundError:
        pass
    folder = venv_root()
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
    return parsedconf['score.init']['based_on']


def _default():
    return os.path.join(confroot(), 'conf', '__default__')
