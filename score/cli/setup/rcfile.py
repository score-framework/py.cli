# vim: set fileencoding=UTF-8
# Copyright © 2015-2017 STRG.AT GmbH, Vienna, Austria
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

from .installer import Installer
import abc
import os
import re
import shutil
import sys
import textwrap


class RcfileModifier(Installer):

    def __init__(self, module_name, rcfile):
        super().__init__(module_name)
        self.rcfile = rcfile
        self.__header = None
        self.__snippet = None

    def test_if_available(self):
        return sys.platform != 'win32'

    def test_if_installed(self):
        return self.snippet in self.read_file('')

    def install(self):
        content = self.read_file()
        blockpos = self._locate_block(content)
        if not content:
            content = self.header + self.snippet
        elif not blockpos:
            if content[-1] == '\n':
                content += '\n'
            else:
                content += '\n\n'
            content += self.header + self.snippet
        else:
            start, end = blockpos
            content = content[:end] + '\n' + self.snippet + content[end:]
        bak = '%s.%s.bak' % (self.rcfile, self.module_name)
        try:
            shutil.copy2(self.rcfile, bak)
        except FileNotFoundError:
            pass
        open(self.rcfile, 'w').write(content)

    def _locate_header(self, content):
        if not content:
            return None
        start = content.find(self.header)
        if start < 0:
            return None
        end = start + len(self.header)
        return (start, end)

    def _locate_block(self, content):
        pos = self._locate_header(content)
        if not pos:
            return None
        start, end = pos
        for line in content[end:].split('\n'):
            if not line.strip() or line.startswith('  '):
                end += len(line) + 1
            else:
                break
        return (start, end)

    @property
    def header(self):
        if self.__header is None:
            header = textwrap.dedent(self.get_header()).lstrip()
            self.__header = header.rstrip() + '\n\n'
        return self.__header

    @property
    def snippet(self):
        if self.__snippet is None:
            snippet = textwrap.dedent(self.get_snippet()).lstrip()
            self.__snippet = textwrap.indent(snippet, '  ').rstrip() + '\n'
        return self.__snippet

    def uninstall(self):
        content = self.read_file()
        blockpos = self._locate_block(content)
        if not blockpos:
            return
        start, end = blockpos
        if content[start:end] == self.header + self.snippet:
            content = content[:start] + content[end:]
        else:
            content = (content[:start] +
                       content[start:end].replace('\n' + self.snippet, '', 1) +
                       content[end:])
        open(self.rcfile, 'w').write(content)

    def get_header(self):
        return r'''
            # The next block was inserted by the `%s' module of
            # The SCORE Framework (http://score-framework.org)
        ''' % self.module_name

    def read_file(self, default=None):
        try:
            return open(self.rcfile).read()
        except FileNotFoundError:
            return default

    @abc.abstractmethod
    def get_snippet(self):
        pass


class BashrcInitializer(RcfileModifier):

    source_re = re.compile(
        '(^|\s+)(\.|source)\s+(~/|(/\w+)+)?\.bashrc', re.MULTILINE)

    def __init__(self, *args):
        super().__init__('score.cli', os.path.expanduser('~/.bash_profile'))

    def get_short_description(self):
        return \
            'Make sure your ~/.bashrc exists and is included in ~/.bash_profile'

    def get_description(self):
        return '''
            This step ensures that you ~/.bashrc file is sourced from your
            ~/.bash_profile. This is required for other installer steps to work
            properly.
            '''

    def test_if_installed(self):
        return self.source_re.search(self.read_file(''))

    def get_snippet(self):
        return r'''
            # This file is sourced by bash for login shells. The following line
            # runs your .bashrc and is recommended by the bash info pages.
            [[ -f ~/.bashrc ]] && . ~/.bashrc'''


class BashrcModifier(RcfileModifier):

    def __init__(self, module_name):
        super().__init__(module_name, os.path.expanduser('~/.bashrc'))

    def install(self):
        if not os.path.exists(self.rcfile):
            initializer = BashrcInitializer('score.cli')
            if not initializer.test_if_installed():
                initializer.install()
        super().install()


class ZshrcModifier(RcfileModifier):

    def __init__(self, module_name):
        super().__init__(module_name, os.path.expanduser('~/.zshrc'))

    def test_if_available(self):
        return super().test_if_available() and os.path.exists(self.rcfile)
