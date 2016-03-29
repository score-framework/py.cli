import os
from pkg_resources import iter_entry_points
import re
import site
import sys
import textwrap


def setup():
    for entrypoint in iter_entry_points(group='score.cli.setup'):
        entrypoint.load()()


def update_path():
    if sys.platform != 'win32':
        # TODO: maybe we should create a bashrc, if there is none?
        _update_bashrc() or _update_bash_profile()
        _update_zshrc()
    else:
        # TODO: some resources for achieving the above on windows:
        # http://stackoverflow.com/questions/2121795/programmatically-modifiy-environment-variables
        # https://docs.python.org/3/library/winreg.html
        pass


def _update_bashrc():
    return _update_rc_file(os.path.expanduser('~/.bashrc'))


def _update_bash_profile():
    return _update_rc_file(os.path.expanduser('~/.bash_profile'))


def _update_zshrc():
    return _update_rc_file(os.path.expanduser('~/.zshrc'))


def _update_rc_file(rcfile):
    try:
        content = open(rcfile).read()
    except FileNotFoundError:
        return False
    # https://docs.python.org/3/install/index.html#alternate-installation-the-user-scheme
    binfolder = os.path.join(site.getuserbase(), 'bin')
    # skip the update, if there is a line adding the binfolder to the path
    path_regex = r'\s*PATH=(.+:)?' + re.escape(binfolder)
    if re.search(path_regex, content):
        return False
    code = '\n'
    if content[-1] != '\n':
        code += '\n'
    code += textwrap.dedent(r'''
        # The next block was inserted by the `cli' module of
        # The SCORE Framework (http://score-framework.org)

            # The following line makes sure that you can access the `score'
            # application in your shell:
            PATH=$PATH:%s
    ''' % binfolder).lstrip()
    open(rcfile, 'a').write(code)
    return True


if __name__ == '__main__':
    setup()
