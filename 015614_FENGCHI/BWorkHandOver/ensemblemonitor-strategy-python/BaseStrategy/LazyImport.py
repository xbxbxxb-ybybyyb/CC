import sys
from types import ModuleType


class LazyModuleType(ModuleType):
    @property
    def _mod(self):
        name = super(LazyModuleType, self).__getattribute__("__name__")
        if name not in sys.modules:
            __import__(name)
        return sys.modules[name]

    def __getattribute__(self, name):
        if name == "_mod":
            return super(LazyModuleType, self).__getattribute__(name)

        try:
            return self._mod.__getattribute__(name)
        except AttributeError:
            return super(LazyModuleType, self).__getattribute__(name)

    def __setattr__(self, name, value):
        self._mod.__setattr__(name, value)


def lazy_import(name, package=None):
    if name.startswith('.'):
        if not package:
            raise TypeError("relative imports require the 'package' argument")
        level = 0
        for character in name:
            if character != '.':
                break
            level += 1

        if not hasattr(package, 'rindex'):
            raise ValueError("'package' not set to a string")
        dot = len(package)
        for _ in range(level, 1, -1):
            try:
                dot = package.rindex('.', 0, dot)
            except ValueError:
                raise ValueError("attempted relative import beyond top-level "
                                 "package")

        name = "{}.{}".format(package[:dot], name[level:])
    return LazyModuleType(name)
