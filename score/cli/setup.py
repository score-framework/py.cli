import os
from pkg_resources import iter_entry_points
import re
import site
import sys
import shutil
import textwrap


def setup():
    for entrypoint in iter_entry_points(group='score.cli.setup'):
        entrypoint.load()()


def _source_bashrc_in_bashprofile():
    source_re = re.compile(
        '(^|\s+)(\.|source)\s+(~/|(/\w+)+)?\.bashrc', re.MULTILINE)

    def test_exists(rcfile, content):
        return source_re.search(content)

    def gen_content():
        return textwrap.dedent(r'''
            # This file is sourced by bash for login shells. The following line
            # runs your .bashrc and is recommended by the bash info pages.
            [[ -f ~/.bashrc ]] && . ~/.bashrc
        ''').lstrip()

    rcfile = os.path.expanduser('~/.bash_profile')
    return append_to_rcfile('cli', rcfile, test_exists, gen_content)


def append_to_bashrc(module, test_exists, gen_content):
    rcfile = os.path.expanduser('~/.bashrc')
    if not os.path.exists(rcfile):
        open(rcfile, 'w')
        _source_bashrc_in_bashprofile()
    return append_to_rcfile(module, rcfile, test_exists, gen_content)


def append_to_zshrc(module, test_exists, gen_content):
    rcfile = os.path.expanduser('~/.zshrc')
    return append_to_rcfile(module, rcfile, test_exists, gen_content)


def append_to_rcfile(module, rcfile, test_exists, gen_content):
    try:
        content = open(rcfile).read()
    except FileNotFoundError:
        return False
    if test_exists(rcfile, content):
        return False
    code = '\n'
    if content and content[-1] != '\n':
        code += '\n'
    code += textwrap.dedent(r'''
        # The next block was inserted by the `%s' module of
        # The SCORE Framework (http://score-framework.org)
    ''' % module).lstrip()
    code += '\n'
    code += textwrap.indent(gen_content(), '  ').rstrip()
    code += '\n'
    bak = '%s.score-%s.bak' % (rcfile, module)
    shutil.copy2(rcfile, bak)
    open(rcfile, 'a').write(code)
    return True


def update_path():
    if sys.platform == 'win32':
        # TODO: some resources for updating the PATH on windows:
        # http://stackoverflow.com/questions/2121795/programmatically-modifiy-environment-variables
        # https://docs.python.org/3/library/winreg.html
        return

    # https://docs.python.org/3/install/index.html#alternate-installation-the-user-scheme
    binfolder = os.path.join(site.getuserbase(), 'bin')

    def test_exists(rcfile, content):
        path_regex = r'\s*PATH=(.+:)?' + re.escape(binfolder)
        return re.search(path_regex, content)

    def gen_content():
        return textwrap.dedent(r'''
            # The following line makes sure that you can access the `score'
            # application in your shell:
            case "$PATH" in
              *{path}*)
                true
                ;;
              *)
                PATH={path}:$PATH
                ;;
            esac
        '''.format(path=binfolder)).lstrip()

    append_to_bashrc('cli', test_exists, gen_content)
    append_to_zshrc('cli', test_exists, gen_content)


if __name__ == '__main__':
    setup()
