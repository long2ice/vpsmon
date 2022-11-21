import importlib
import inspect
import pkgutil
from typing import Type

from vpsmon import providers
from vpsmon.providers import Provider, ProviderType


def _discover_providers():
    ret = {}
    for m in pkgutil.iter_modules(providers.__path__):
        mod = importlib.import_module(f"{providers.__name__}.{m.name}")
        for _, member in inspect.getmembers(mod, inspect.isclass):
            if issubclass(member, Provider) and member is not Provider and member.enable:
                ret[member.type] = member
    return ret


_providers = _discover_providers()


def get_provider(type_: ProviderType) -> Type[Provider]:
    return _providers[type_]


def get_providers():
    return _providers.values()
