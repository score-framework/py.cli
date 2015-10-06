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
import os
import re
import sys
from .config import config_file


ZSH_COMPLETION_SCRIPT = r'''

autoload bashcompinit
bashcompinit

%(complete_func)s() {
    COMPREPLY=$(\
        _COMP_WORDS="${COMP_WORDS[*]}";\
        _COMP_CWORD="$COMP_CWORD";\
        typeset +r COMP_WORDS;\
        typeset +r COMP_CWORDS;\
        COMP_CWORD=$_COMP_CWORD \
            COMP_WORDS="$_COMP_WORDS" \
            %(autocomplete_var)s=complete $1\
    )
    return 0
}

complete -F %(complete_func)s -o default %(script_names)s

'''


@click.group('autocomplete')
def main():
    """
    Manages shell completion installation.
    """
    pass


@main.command('install-bash')
@click.option('-g', '--global', 'global_', is_flag=True,
              help='Install into /etc/bash_completion.d/')
def install_bash(global_):
    """
    Installs command completion for bash.

    Will add the completion file to ~/.bashrc, unless -g was provided.
    """
    file = config_file('autocomplete/bash', home=True)
    if not os.path.exists(file):
        from click._bashcomplete import get_completion_script
        prog_name = os.path.basename(sys.argv and sys.argv[0] or __file__)
        complete_var = '_%s_COMPLETE' % (prog_name.replace('-', '_')).upper()
        open(file, 'w').write(get_completion_script(prog_name, complete_var))
    if global_:
        os.symlink(file, '/etc/bash_completion.d/score.sh')
        return
    home = os.getenv('HOME')
    bashrc = os.path.join(home, '.bashrc')
    content = open(bashrc).read()
    regex = r'^\s*(source|\.)\s+%s\s*$' % re.escape(file)
    if re.search(regex, content, re.MULTILINE):
        return
    with open(bashrc, 'a') as fp:
        fp.write('\n\n# score autocompletion\n')
        fp.write('source %s\n' % file)


@main.command('install-zsh')
def install_zsh():
    """
    Installs command completion for zsh.
    """
    file = config_file('autocomplete/zsh', home=True)
    if not os.path.exists(file):
        prog_name = os.path.basename(sys.argv and sys.argv[0] or __file__)
        complete_var = '_%s_COMPLETE' % (prog_name.replace('-', '_')).upper()
        script = ZSH_COMPLETION_SCRIPT % {
            'complete_func': '_%s_completion' % prog_name,
            'script_names': prog_name,
            'autocomplete_var': complete_var,
        }
        open(file, 'w').write(script)
    home = os.getenv('HOME')
    zshrc = os.path.join(home, '.zshrc')
    content = open(zshrc).read()
    regex = r'^\s*(source|\.)\s+%s\s*$' % re.escape(file)
    if re.search(regex, content, re.MULTILINE):
        return
    with open(zshrc, 'a') as fp:
        fp.write('\n\n# score autocompletion\n')
        fp.write('source %s\n' % file)


if __name__ == '__main__':
    main()
