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
import re
from setuptools import setup
from setuptools.command.install import install
from setuptools.command.develop import develop
import sys
import textwrap


class ShellUpdateMixin:

    def run(self):
        result = super().run()
        home = os.getenv('HOME') or os.getenv('HOMEPATH')
        confroot = os.path.join(home, '.score')
        globalconf = os.path.join(confroot, 'conf', '__global__')
        defaultconf = os.path.join(confroot, 'conf', '__default__')
        self._install_global_conf(globalconf)
        self._install_default_conf(defaultconf, globalconf)
        is_virtualenv = (
            hasattr(sys, 'real_prefix') or (
                hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))
        if not is_virtualenv:
            # we are outside a virtual environment
            # FIXME: we should be checking, if this is a --user installation,
            # but we have not found a reliable, cross-platform way of doing that
            self._update_bashrc() or self._update_bash_profile()
            self._update_zshrc()
        return result

    def _install_global_conf(self, file):
        try:
            os.makedirs(os.path.dirname(file), exist_ok=True)
            open(file, 'x').write(textwrap.dedent('''
                # This is the global CLI configuration file for your SCORE
                # installation. The values defined here will be available in
                # *all* your command line applications.
            ''').strip())
        except FileExistsError:
            pass

    def _install_default_conf(self, file, globalconf):
        try:
            os.makedirs(os.path.dirname(file), exist_ok=True)
            open(file, 'x').write(textwrap.dedent('''
                [score.init]
                based_on = %s
            ''' % globalconf).strip())
        except FileExistsError:
            pass

    def _update_bashrc(self):
        prompt = textwrap.dedent(r'''
            if [ -n "$VIRTUAL_ENV" ]; then
              export PS1="\[[0;33m\](${VIRTUAL_ENV##*/})\[[0m\] $PS1"
            fi
        ''').strip()
        return self._update_rc_file(os.path.expanduser('~/.bashrc'), prompt)

    def _update_bash_profile(self):
        prompt = textwrap.dedent(r'''
            if [ -n "$VIRTUAL_ENV" ]; then
              export PS1="\[[0;33m\](${VIRTUAL_ENV##*/})\[[0m\] $PS1"
            fi
        ''').strip()
        return self._update_rc_file(os.path.expanduser('~/.bash_profile'),
                                    prompt)

    def _update_zshrc(self):
        prompt = textwrap.dedent(r'''
            if [ -n "$VIRTUAL_ENV" ]; then
              export PROMPT="%{[0;33m%}(${VIRTUAL_ENV##*/})%{[0m%} $PROMPT"
            fi
        ''').strip()
        return self._update_rc_file(os.path.expanduser('~/.zshrc'), prompt)

    def _update_rc_file(self, rcfile, prompt):
        try:
            content = open(rcfile).read()
        except FileNotFoundError:
            return False
        binfolder = self._bin_folder()
        if not binfolder:
            # probably windows, wouldn't even know how to modify the PATH
            return False
        # skip the update, if there is a line adding the binfolder to the path
        path_regex = r'\s*PATH=(.+:)?' + re.escape(binfolder)
        if re.search(path_regex, content):
            return False
        code = '\n'
        if content[-1] != '\n':
            code += '\n'
        code += textwrap.dedent(r'''
            # The next two blocks were inserted by the `projects' module of
            # The SCORE Framework (http://score-framework.org)

        ''').lstrip()
        code += textwrap.indent(textwrap.dedent(r'''
            # The following line makes sure that you can access the `score'
            # application in your shell:
            PATH=$PATH:%s

            # The next line updates your shell prompt to include the name of
            # the current project.
        ''' % binfolder).lstrip(), '  ')
        code += textwrap.indent(prompt, '  ') + '\n'
        open(rcfile, 'a').write(code)
        return True

    def _bin_folder(self):
        if sys.platform == 'darwin':
            # mac os x
            return os.path.expanduser(
                '~/Library/Python/%d.%d/bin' % (sys.version_info.major,
                                                sys.version_info.minor))
        elif sys.platform in ('linux', 'freebsd', 'cygwin'):
            return os.path.expanduser('~/.local/bin')
        else:
            return None


class InstallCommand(ShellUpdateMixin, install):
    pass


class DevelopCommand(ShellUpdateMixin, develop):
    pass


here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

setup(
    name='score.cli',
    version='0.2.6',
    description='Command line interface to The SCORE Framework',
    long_description=README,
    author='strg.at',
    author_email='score@strg.at',
    url='http://score-framework.org',
    keywords='score framework cli click',
    packages=['score', 'score.cli'],
    namespace_packages=['score'],
    zip_safe=False,
    license='LGPL',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General '
            'Public License v3 or later (LGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    install_requires=[
        'click',
        'score.init',
    ],
    entry_points={
        'console_scripts': [
            'score = score.cli:main'
        ],
        'score.cli': [
            'conf = score.cli.cli:main',
        ]
    },
    cmdclass={
        'install': InstallCommand,
        'develop': DevelopCommand,
    }
)
