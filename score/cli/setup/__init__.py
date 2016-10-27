from .installer import Installer
from .rcfile import RcfileModifier, BashrcModifier, ZshrcModifier
from .path import AddToWindowsPath, AddToBashrcPath, AddToZshrcPath
from .main import main


__all__ = ('Installer', 'RcfileModifier', 'BashrcModifier', 'ZshrcModifier',
           'AddToWindowsPath', 'AddToBashrcPath', 'AddToZshrcPath', 'main')


if __name__ == '__main__':
    main()
