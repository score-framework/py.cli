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

import sys


class ConsoleUI:

    def __call__(self, installers):
        self.installers = list(sorted(i for i in installers if i.is_available))
        print('\nWelcome to the command line setup of The SCORE Framework.')
        while self.prompt_main():
            pass

    def prompt_main(self):
        print('')
        for i, installer in enumerate(self.installers):
            char = '✓' if installer.is_installed else ' '
            print('%s %d. %s' % (char, i + 1, installer.short_description))
        print('  q. Exit\nChoose an action: ', end='')
        x = self.read_input()
        if x == 'q':
            return False
        try:
            x = int(x)
            installer = self.installers[x - 1]
        except:
            return True
        while self.prompt_installer(installer):
            pass
        return True

    def prompt_installer(self, installer):
        print('\n' + installer.description, end='')
        if installer.is_installed:
            print('This feature is already installed. '
                  'Do you want to remove it? ', end='')
            if self.read_bool(False):
                installer.uninstall()
        else:
            print('Continue?')
            if self.read_bool(True):
                installer.install()
        return False

    def read_bool(self, default):
        if default:
            print('[Yn] ', end='')
        else:
            print('[yN] ', end='')
        x = self.read_input()
        if x == '':
            return default
        elif x == 'y':
            return True
        elif x == 'n':
            return False
        print('Invalid input')
        return self.read_bool(default)

    def read_input(self):
        try:
            return input()
        except KeyboardInterrupt:
            print('')
            sys.exit(0)


default = ConsoleUI()
