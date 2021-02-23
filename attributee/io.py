
import os
import sys
import typing
import collections
import argparse
from functools import partial

from attributee import Attributee, AttributeException, is_undefined, Boolean

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

    def _no_support():
        raise ImportError("PyYAML not installed")

    dump_yaml = lambda a, b: _no_support()
    load_yaml = lambda a, b: _no_support()
    pass


import json

dump_json = partial(_dump_serialized, dumper=partial(json.dump))
load_json = partial(_load_serialized, loader=partial(json.load, object_pairs_hook=collections.OrderedDict))

class Entrypoint(object):
    """ A mixin that provides initialization of Attributee object using command line arguments.

    """

    @classmethod
    def parse(cls, boolean_flags=None):
        """[summary]

        Args:
            boolean_flags (bool, optional): [description]. Defaults to True.

        Raises:
            AttributeException: [description]

        Returns:
            [type]: [description]
        """
        if not issubclass(cls, Attributee):
            raise AttributeException("Not a valid base class")

        if boolean_flags is None:
            boolean_flags = os.environ.get("ATTIRBUTEE_ARGPARSE_BOOLEAN", "false").lower() in ("true", "1")

        args = dict()

        parser = argparse.ArgumentParser()

        for name, attr in cls.attributes().items():
            data = {}
            if isinstance(attr, Boolean) and boolean_flags:
                if not is_undefined(attr.default) and attr.default is True:
                    data["action"] = "store_false"
                    data["dest"] = name
                    name = "not_" + name
                else:
                    data["action"] = "store_true"
                data["required"] = False
            elif not is_undefined(attr.default):
                data["default"] = attr.default
                data["required"] = False
            else:
                data["required"] = True
            if attr.description is not None:
                data["help"] = attr.description

            parser.add_argument("--" + name, **data)

        args = parser.parse_args()

        return cls(**vars(args))

class Serializable(object):
    """ A mixin that provides handy IO methods for Attributtee derived classes.

    """

    @classmethod
    def read(cls, source: str):
        if not issubclass(cls, Attributee):
            raise AttributeException("Not a valid base class")
        ext = os.path.splitext(source)[1].lower()
        if ext in [".yml", ".yaml"]:
            return load_yaml(source, cls)
        if ext in [".json"]:
            return load_json(source, cls)
        else:
            raise AttributeException("Unknown file format")


    def write(self, destination: str):
        if not isinstance(self, Attributee):
            raise AttributeException("Not a valid base class")
        ext = os.path.splitext(destination)[1].lower()
        if ext in [".yml", ".yaml"]:
            return dump_yaml(self, destination)
        if ext in [".json"]:
            return dump_json(self, destination)
        else:
            raise AttributeException("Unknown file format")


