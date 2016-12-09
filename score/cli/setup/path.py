from .installer import Installer
from .rcfile import BashrcModifier, ZshrcModifier
import os
import re
import site
import sys
import textwrap


if site.USER_BASE is None:
    site.getuserbase()


class AddToWindowsPath(Installer):

    def test_if_available(self):
        return sys.platform == 'win32'

    def test_if_installed(self):
        return False

    def get_short_description(self):
        return "Configure PATH to `score'"

    def get_description(self):
        return '''
            This step will add the path to your SCORE installation to your PATH.
            This will make sure that you can then access the `score' application
            in your shell.

            Unfortunately this step has not been automated yet due to lack of
            windows machines. If you choose to perform this installation, it
            will raise NotImplemented.
            '''

    def install(self):
        # TODO: some resources for updating the PATH on windows:
        # http://stackoverflow.com/questions/2121795/programmatically-modifiy-environment-variables
        # https://docs.python.org/3/library/winreg.html
        raise NotImplemented(
            'Unfortunately, we do not have windows support yet')

    def uninstall(self):
        assert False, "Should never be here since " \
            "test_if_installed() always returns False"


class AddToBashrcPath(BashrcModifier):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.binfolder = os.path.join(site.USER_BASE, 'bin')

    def test_if_installed(self):
        path_regex = r'\s*PATH=(.+:)?' + re.escape(self.binfolder)
        return re.search(path_regex, self.read_file(''))

    def get_short_description(self):
        return "Configure PATH to `score' in your ~/.bashrc"

    def get_description(self):
        return '''
            This step will update your ~/.bashrc file to add the location of the
            SCORE installation to your PATH. This will make sure that you can
            then access the `score' application in your shell.

            We will create a backup of your ~/.bashrc file before changing it,
            But if you are not comfortable with automatically modifying your
            bash configuration file, you can add these lines manually:

              ''' + textwrap.indent(self.snippet, '            ').lstrip()

    def get_snippet(self):
        return r'''
            # The following line makes sure that you can access the `score'
            # application in your shell:
            case "$PATH" in
              *{dir}*)
                true
                ;;
              *)
                PATH={dir}:$PATH
                ;;
            esac
        '''.format(dir=self.binfolder)


class AddToZshrcPath(ZshrcModifier):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.binfolder = os.path.join(site.USER_BASE, 'bin')

    def get_short_description(self):
        return "Configure PATH to `score' in your ~/.zshrc"

    test_if_installed = AddToBashrcPath.test_if_installed

    def get_description(self):
        return AddToBashrcPath.get_description(self).\
            replace('~/.bashrc', '~/.zshrc')

    get_snippet = AddToBashrcPath.get_snippet
