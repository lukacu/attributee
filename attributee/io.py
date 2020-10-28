
import typing
import collections
from functools import partial

from attributee import Attributee

def _dump_serialized(obj: Attributee, handle: typing.Union[typing.IO[str], str], dumper: typing.Callable):
    data = obj.dump()

    if isinstance(handle, str):
        with open(handle, "w") as stream:
            dumper(data, stream)
    else:
        dumper(data, handle)

def _load_serialized(handle: typing.Union[typing.IO[str], str], factory: typing.Callable, loader: typing.Callable):
    if isinstance(handle, str):
        with open(handle, "r") as stream:
            data = loader(stream)
    else:
        data = loader(stream)

    return factory(**data)

try:

    import yaml

    def _yaml_load(stream):
        class OrderedLoader(yaml.Loader):
            pass
        def construct_mapping(loader, node):
            loader.flatten_mapping(node)
            return collections.OrderedDict(loader.construct_pairs(node))
        OrderedLoader.add_constructor(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            construct_mapping)
        return yaml.load(stream, OrderedLoader)

    def _yaml_dump(data, stream=None, **kwds):
        class OrderedDumper(yaml.Dumper):
            pass
        def _dict_representer(dumper, data):
            return dumper.represent_mapping(
                yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
                data.items())
        OrderedDumper.add_representer(collections.OrderedDict, _dict_representer)
        return yaml.dump(data, stream, OrderedDumper, **kwds)

    dump_yaml = partial(_dump_serialized, dumper=_yaml_dump)
    load_yaml = partial(_load_serialized, loader=_yaml_load)

except ImportError:
    pass


import json

dump_json = partial(_dump_serialized, dumper=partial(json.dump))
load_json = partial(_load_serialized, loader=partial(json.load, object_pairs_hook=collections.OrderedDict))
