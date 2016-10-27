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
