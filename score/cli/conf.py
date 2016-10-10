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

import os
import sys
import re
from score.init import parse_config_file as parse
from collections import OrderedDict
import textwrap


class InvalidConfigurationNameException(ValueError):
    """
    Raised when a configuration is registered with a bogus name.
    """


def venv_root(venv=None):
    """
    Provides the root folder of the current virtual environment.

    Returns `None`, if this python process is not running inside a virtual
    environment.

    In order to provide a similar interface to the other functions in this
    package, it also accepts a *venv* parameter. Since that parameter is
    expected to be the root of a virtual environment, it will be returned, if it
    is passed.
    """
    if venv is not None:
        return venv
    if hasattr(sys, 'real_prefix'):
        return sys.prefix
    if hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix:
        return sys.prefix
    return None


def rootdir(*, global_=False, venv=None):
    """
    Provides the current ``.score`` folder.

    This function will determine the valid path of the configuration folder for
    the current environment, as described in the narrative documentation of the
    :ref:`configuration locations <score_cli_config_locations>`.

    It is possible to retrieve the configuration folder in one's home directory
    by passing a truthy value for *global_*.

    It is also possible to access the configuration folder of a different
    virtual environment by passing the *venv* parameter (the path to a virtual
    environment).
    """
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


def add(name, path, *, venv=None):
    """
    Adds a configuration with given *name*, pointing to the configuration file
    at *path*.

    The name must not start with two underscores, must consist of alphanumeric
    characters, underscores and hyphens and must not start with a number or a
    hyphen. Will raise an InvalidConfigurationNameException violates these
    constraints.

    Can also operate on a given virtual environment if the *venv* parameter is
    not `None`. The specifics of this behaviour is documented in
    :func:`.rootdir`.
    """
    if name.startswith('__') or not re.match('^[a-zA-Z_][a-zA-Z0-9_-]*$', name):
        raise InvalidConfigurationNameException(name)
    root = rootdir(venv=venv)
    root = os.path.join(root, 'conf')
    os.makedirs(root, exist_ok=True)
    file = os.path.join(root, name)
    open(file, 'w').write(textwrap.dedent('''
        [score.init]
        based_on =
            %s
            %s
        ''' % (global_file(), path)))


def remove(name, *, venv=None):
    """
    Deletes the configuration with given *name*.

    Can also operate on a given virtual environment if the *venv* parameter is
    not `None`. The specifics of this behaviour is documented in
    :func:`.rootdir`.
    """
    file = os.path.join(rootdir(venv=venv), 'conf', name)
    try:
        os.unlink(file)
    except FileNotFoundError:
        pass


def make_default(name, *, venv=None):
    """
    Updates the current environment's default configuration to point to the
    configuration with given *name*.

    Can also operate on a given virtual environment if the *venv* parameter is
    not `None`. The specifics of this behaviour is documented in
    :func:`.rootdir`.
    """
    root = rootdir(venv=venv)
    file = os.path.join(root, 'conf', name)
    if not os.path.exists(file):
        raise FileNotFoundError(file)
    open(default_file(venv=venv), 'w').write(textwrap.dedent('''
        [score.init]
        based_on =
            ${here}/%s
    ''' % name).lstrip())


def get_file(name, *, venv=None):
    """
    Returns the file the configuration with given *name* is pointing to.

    Can also operate on a given virtual environment if the *venv* parameter is
    not `None`. The specifics of this behaviour is documented in
    :func:`.rootdir`.
    """
    return name2file(venv=venv)[name]


def get_default(*, venv=None):
    """
    Returns the name of the default configuration.

    Can also operate on a given virtual environment if the *venv* parameter is
    not `None`. The specifics of this behaviour is documented in
    :func:`.rootdir`.
    """
    try:
        return os.path.basename(get_origin(default_file(venv=venv)))
    except FileNotFoundError:
        return None


def name2file(*, include_global=True, venv=None):
    """
    Returns the names of all available configurations.

    Will list all configurations in the current virtual environment, as well as
    all global configuration files, unless *include_global* is `False`.

    Can also operate on a given virtual environment if the *venv* parameter is
    not `None`. The specifics of this behaviour is documented in
    :func:`.rootdir`.
    """
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


def global_file():
    """
    Returns the path to the global configuration file.

    Although the return value of this function is always the same, it ensures
    that the file actually exists by creating it with some informative comments.
    """
    file = os.path.join(rootdir(global_=True), 'conf', '__global__')
    os.makedirs(os.path.dirname(file), exist_ok=True)
    try:
        open(file, 'x').write(textwrap.dedent('''
            # This is the global CLI configuration file for your SCORE
            # installation. The values defined here will be available in
            # *all* your command line applications.
        ''').lstrip())
    except FileExistsError:
        pass
    return file


def default_file(*, global_=False, venv=None):
    """
    Returns the path to the default configuration in the current environment.

    This function will create that file, if it does not exist.

    Can also operate on a given virtual environment if the *venv* parameter is
    not `None`. The specifics of this behaviour is documented in
    :func:`.rootdir`.
    """
    file = os.path.join(rootdir(global_=global_, venv=venv),
                        'conf', '__default__')
    os.makedirs(os.path.dirname(file), exist_ok=True)
    try:
        open(file, 'x').write(textwrap.dedent('''
            [score.init]
            based_on = %s
        ''' % global_file()).lstrip())
    except FileExistsError:
        pass
    return file


def get_origin(file):
    """
    Parses given configuration file and finds the file this one is
    :func:`based_on <score.init.parse_config_file>`.
    """
    parsedconf = parse(file, recurse=False)
    base = parsedconf['score.init']['based_on']
    if '\n' in base:
        base = base.split('\n')[-1]
    return base
