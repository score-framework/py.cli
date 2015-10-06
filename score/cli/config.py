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
import configparser
import os
import sys


NO_VALUE = type('NO_VALUE', (object,), {})()


class ConfigSection:
    """
    The section of a :class:`.Config` object.
    """

    def __init__(self, config, section, fallback):
        self.config = config
        self.section = section
        self.fallback = fallback
        self.cache = {}

    def __contains__(self, key):
        if key in self.cache:
            return self.cache[key] != '__unset__'
        if key in self.section:
            return self.section[key] != '__unset__'
        return self.fallback and key in self.fallback

    def __getitem__(self, key):
        value = None
        if key in self.cache:
            value = self.cache[key]
        elif key in self.section:
            value = self.section[key]
        if value == '__unset__':
            raise IndexError()
        if value is not None:
            return value
        if self.fallback is None:
            raise IndexError()
        return self.fallback.__getitem__(key)

    def __setitem__(self, key, value):
        self.cache[key] = value

    def __delitem__(self, key):
        if key in self.cache:
            del self.cache[key]
        if key in self.section:
            del self.section[key]
        if self.fallback and key in self.fallback:
            self.__setitem__(key, '__unset__')

    def __iter__(self):
        return iter(self.keys())

    def __len__(self):
        return len(self.keys())

    def get(self, key, fallback=NO_VALUE):
        if fallback == NO_VALUE:
            return self.cache[key]
        return self.cache.get(key, fallback)

    def keys(self):
        keys = set()
        if self.fallback is not None:
            for k in self.fallback:
                keys.add(k)
        for k in self.section:
            if self.section[k] == '__unset__':
                keys.remove(k)
            else:
                keys.add(k)
        for k in self.cache:
            if self.cache[k] == '__unset__':
                keys.remove(k)
            else:
                keys.add(k)
        return keys

    def update(self, other):
        for k, v in other.items():
            self[k] = v

    def flush(self):
        for k, v in self.cache.items():
            self.section[k] = v

    def persist(self):
        self.config.flush(section=self)


class Config:
    """
    Wrapper around a :class:`configparser.ConfigParser` that allows reading
    values from a fallback configuration, but writes to the file it was
    initialized with.
    """

    def __init__(self, file, fallback=None):
        self.file = file
        self.cfg = configparser.ConfigParser()
        self.cfg.read(file)
        self.fallback = fallback
        self._sections = {}
        self.cache = {}

    def __getitem__(self, key):
        if key in self._sections:
            return self._sections[key]
        if key in self.cache:
            section = self.cache[key]
        elif key in self.cfg:
            section = self.cfg[key]
        else:
            self.cache[key] = {}
            section = self.cache[key]
        fallback = None
        if self.fallback:
            fallback = self.fallback.__getitem__(key)
        self._sections[key] = ConfigSection(self, section, fallback)
        return self._sections[key]

    def __setitem__(self, key, value):
        for k, v in value:
            self[key][k] = v

    def __contains__(self, key):
        if key in self.cache:
            return True
        if key in self.cfg:
            return True
        return self.fallback and key in self.fallback

    def __delitem__(self, key):
        if key in self.cache:
            del self.cache[key]
        if key in self._sections:
            del self._sections[key]
        if key in self.cfg:
            del self.cfg[key]

    def __len__(self):
        return len(self.sections())

    def __iter__(self):
        return iter(self.sections())

    def get(self, key, fallback=None):
        if key in self.cache:
            return self.cache[key]
        if key in self.cfg:
            return self.cfg[key]
        if self.fallback and key in self.fallback:
            return self.fallback[key]
        return fallback

    def sections(self):
        names = set()
        if self.fallback:
            for section in self.fallback.sections():
                names.add(section)
        for section in self.cfg.sections():
            if len(self[section]):
                names.add(section)
            elif section in names:
                names.remove(section)
        for section in self._sections:
            if len(self._sections[section]):
                names.add(section)
            elif section in names:
                names.remove(section)
        return names

    def keys(self):
        return self.sections()

    def values(self):
        return [self[key] for key in self.sections()]

    def flush(self, section=None):
        if isinstance(section, ConfigSection):
            section = next(k for k, v in self._sections if v == section)
        if not section:
            for section in self._sections:
                self.flush(section)
            return
        if section not in self._sections:
            if section in self:
                return
            raise IndexError()
        self._sections[section].flush()
        if section not in self.cache or not self.cache[section]:
            return
        if section not in self.cfg:
            self.cfg[section] = {}
        for k, v in self.cache[section].items():
            self.cfg[section][k] = v
        del self.cache[section]

    def persist(self):
        self.flush()
        self.cfg.write(open(self.file, 'w'))


@click.group('config')
def main():
    """
    Manages configuration values.
    """
    pass


@main.command('set')
@click.option('-g', '--global', 'global_', is_flag=True, default=False)
@click.argument('section')
@click.argument('key')
@click.argument('value')
def config_set(global_, section, key, value):
    """
    Sets a configuration value.
    """
    cfg = config(global_=global_)
    cfg[section][key] = value
    cfg.persist()


@main.command('del')
@click.option('-g', '--global', 'global_', is_flag=True, default=False)
@click.argument('section')
@click.argument('key', required=False)
def config_del(global_, section, key=None):
    """
    Remove a configuration value.
    """
    cfg = config(global_=global_)
    if key:
        del cfg[section][key]
    else:
        del cfg[section]
    cfg.persist()


@main.command('list')
@click.option('-g', '--global', 'global_', is_flag=True, default=False)
@click.argument('section', required=False)
def config_list(global_, section=None):
    """
    Lists all available configuration values.
    """
    cfg = config(global_=global_)
    if section:
        for k in sorted(cfg[section]):
            print('%s = %s' % (k, cfg[section][k]))
    else:
        for section in sorted(cfg):
            print('[%s]' % section)
            for k in sorted(cfg[section]):
                print('%s = %s' % (k, cfg[section][k]))
            print('')


def config(section=None, *, global_=False):
    """
    Provides a configuration object that has a similar structure as a
    :class:`configparser.ConfigParser`. Example usage:

    .. code-block:: python

        conf = config()
        conf['section'][key] = value
        del conf['section']['obsolete_key']
        del conf['obsolete_section']
        conf.persist()

    It is possible to fetch a specific *section* view by passing the parameter
    with the same name. The following methods of configuration retrieval are
    thus equivalent:

    .. code-block:: python

        config()['section'] == config('section')

    If this process is running inside a virtual environment, and the *global_*
    parameter evaluates to `False`, the returned object will aggregate the
    virtualenv-specific configuration and the global configuration. Any
    configuration present in either file will be visible in the returned object.
    Changes will only be stored in the virtualenv-specific file, though.

    All the restrictions described in the previous paragraph can be circumvented
    by providing a `True` value for the *global_* parameter.
    """
    cfg = Config(config_file('score.ini', global_=True))
    if not global_ and (hasattr(sys, 'real_prefix') or
                        hasattr(sys, 'base_prefix')):
        cfg = Config(config_file('score.ini', global_=False), fallback=cfg)
    if section is not None:
        return cfg[section]
    return cfg


def config_file(name, create=True, global_=False):
    """
    Provides the path to a file inside the configuration folder. The format and
    usage of the file is up to the calling instance. The rules for the exact
    location of the file follow the usual algorithm described in
    :func:`.config_folder`, for example.

    It is highly recommended that any module making use of this function writes
    all its configuration files into a dedicated sub-folder to prevent name
    clashes:

    >>> file = config_file('modulename/myfile.xml')
    """
    folder = None
    if '/' in name:
        folder = os.path.dirname(name)
        name = os.path.basename(name)
    return os.path.join(config_folder(folder, create, global_), name)


def config_folder(name=None, create=True, global_=False):
    """
    Provides the path to the folder containing the current configuration. This
    corresponds to the folder ``~/.score`` by default, but changes to
    ``$VIRTUAL_ENV/.score``, if this process is running inside a virtual
    environment and the *global_* parameter evaluates to `False`.

    It can also return a folder within the configuration folder described above,
    if the *name* parameter is given.

    The returned folder will be created automatically, if the value of *create*
    is left at its default value.
    """
    if global_:
        root = os.getenv('HOME') or os.getenv('HOMEPATH')
    elif hasattr(sys, 'real_prefix') and os.access(sys.real_prefix, os.W_OK):
        root = sys.real_prefix
    elif hasattr(sys, 'base_prefix') and os.access(sys.base_prefix, os.W_OK):
        root = sys.base_prefix
    else:
        root = os.getenv('HOME') or os.getenv('HOMEPATH')
    root = os.path.join(root, '.score')
    if name:
        folder = os.path.join(root, name)
        if os.path.commonprefix(folder, root) != root:
            raise ValueError('Invalid path "%s"' % name)
    else:
        folder = root
    if create:
        os.makedirs(folder, exist_ok=True)
    return folder


if __name__ == '__main__':
    main()
