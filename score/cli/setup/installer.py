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

import abc
import textwrap


class Installer(abc.ABC):

    def __init__(self, module_name):
        self.module_name = module_name
        self.__description = None
        self.__short_description = None
        self.__is_available = None
        self.__is_installed = None

    @property
    def description(self):
        if self.__description is None:
            description = textwrap.dedent(self.get_description()).lstrip()
            self.__description = description.strip() + '\n\n'
        return self.__description

    @property
    def short_description(self):
        if self.__short_description is None:
            short_description = textwrap.dedent(self.get_short_description())
            self.__short_description = short_description.strip()
        return self.__short_description

    @property
    def is_available(self):
        if self.__is_available is None:
            self.__is_available = self.test_if_available()
        return self.__is_available

    @property
    def is_installed(self):
        return self.test_if_installed()

    def __lt__(self, other):
        if not isinstance(other, Installer):
            return super() < other
        if self.module_name != other.module_name:
            return self.module_name < other.module_name
        return self.short_description < other.short_description

    def test_if_available(self):
        return True

    @abc.abstractmethod
    def test_if_installed(self):
        pass

    @abc.abstractmethod
    def get_description(self):
        pass

    @abc.abstractmethod
    def get_short_description(self):
        pass

    @abc.abstractmethod
    def install(self):
        pass

    @abc.abstractmethod
    def uninstall(self):
        pass
