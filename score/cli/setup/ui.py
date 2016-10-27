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
