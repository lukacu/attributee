


try:
    # Python 3.10 changes
    from collections.abc import Iterable, Mapping, Sequence
except ImportError:
    from collections import Iterable, Mapping, Sequence

from attributee import Attribute, AttributeException, CoerceContext

def _readonly(*args, **kwargs):
    raise AttributeException("Content is readonly")

class ReadonlySequence(Sequence):

    def __init__(self, data):
        self._data = data

    def __getitem__(self, index):
        return self._data[index]

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    append = _readonly
    __add__ = _readonly
    insert = _readonly
    __setitem__ = _readonly

class CoerceSequence(ReadonlySequence):

    def __init__(self, data, parent, type):
        super().__init__(data)
        self._parent = parent
        self._type = type

    def append(self, item):
        ctx = CoerceContext(parent=self._parent, key=len(self._data))
        self._data.append(self._type.coerce(item, ctx))

    def __add__(self, item):
        self.append(item)

    def insert(self, index, value):
        ctx = CoerceContext(parent=self._parent, key=index)
        self._data.insert(index, self._type.coerce(value, ctx))

    def __setitem__(self, index, value):
        ctx = CoerceContext(parent=self._parent, key=index)
        self._data[index] = self._type.coerce(value, ctx)

class ReadonlyMapping(Mapping):

    def __init__(self, data):
        self._data = data

    def __getitem__(self, key):
        return self._data[key]

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    __setitem__ = _readonly

class CoerceMapping(ReadonlyMapping):

    def __init__(self, data, parent, type):
        super().__init__(data)
        self._parent = parent
        self._type = type

    def __setitem__(self, key, value):
        ctx = CoerceContext(parent=self._parent, key=key)
        self._data[key] = self._type.coerce(value, ctx)

class Tuple(Attribute):

    def __init__(self, *types, separator=",", **kwargs):
        super().__init__(**kwargs)
        for t in types:
            if not isinstance(t, Attribute):
                raise AttributeException("Illegal base class {}".format(t))

        self._types = types
        self._separator = separator

    def coerce(self, value, context=None):
        if isinstance(value, str):
            value = value.split(self._separator)
        if isinstance(value, dict):
            value = value.values()
        if not isinstance(value, Iterable):
            raise AttributeException("Unable to value convert to list")
        parent = context.parent if context is not None else None
        return tuple([t.coerce(x, CoerceContext(parent=parent, key=i)) for i, (x, t) in enumerate(zip(value, self._types))])

    def __iter__(self):
        # This is only here to avoid pylint errors for the actual attribute field
        raise NotImplementedError

    def __getitem__(self, key):
        # This is only here to avoid pylint errors for the actual attribute field
        raise NotImplementedError

    def __setitem__(self, key, value):
        # This is only here to avoid pylint errors for the actual attribute field
        raise NotImplementedError

    def dump(self, value):
        return tuple([t.dump(x) for x, t in zip(value, self._types)])

    @property
    def types(self):
        return tuple(self._types)

class List(Attribute):

    def __init__(self, contains, separator=",", **kwargs):
        if not isinstance(contains, Attribute): raise AttributeException("Container should be an Attribute object")
        self._separator = separator
        self._contains = contains
        super().__init__(**kwargs)

    def coerce(self, value, context=None):
        if isinstance(value, str):
            value = [v.strip() for v in value.split(self._separator)]
        if isinstance(value, dict):
            value = value.values()
        if not isinstance(value, Iterable):
            raise AttributeException("Unable to convert value to list")
        parent = context.parent if context is not None else None
        data = [self._contains.coerce(x, CoerceContext(parent=parent, key=i)) for i, x in enumerate(value)]
        if self.readonly:
            return ReadonlySequence(data)
        else:
            return CoerceSequence(data, self, self._contains)

    def __iter__(self):
        # This is only here to avoid pylint errors for the actual attribute field
        raise NotImplementedError

    def __getitem__(self, key):
        # This is only here to avoid pylint errors for the actual attribute field
        raise NotImplementedError

    def __setitem__(self, key, value):
        # This is only here to avoid pylint errors for the actual attribute field
        raise NotImplementedError

    def dump(self, value):
        return [self._contains.dump(x) for x in value]

    @property
    def contains(self):
        return self._contains

class Map(Attribute):

    def __init__(self, contains, container=dict, **kwargs):
        if not isinstance(contains, Attribute): raise AttributeException("Container should be an Attribute object")
        self._contains = contains
        self._container = container
        super().__init__(**kwargs)

    def coerce(self, value, context=None):
        if not isinstance(value, Mapping):
            raise AttributeException("Unable to value convert to dict")
        container = self._container()
        for name, data in value.items():
            ctx = CoerceContext(parent=context.parent if context is not None else None, key=name)
            container[name] = self._contains.coerce(data, ctx)
        if self.readonly:
            return ReadonlyMapping(container)
        else:
            return CoerceMapping(container, self, self._contains)

    def __iter__(self):
        # This is only here to avoid pylint errors for the actual attribute field
        raise NotImplementedError

    def __getitem__(self, key):
        # This is only here to avoid pylint errors for the actual attribute field
        raise NotImplementedError

    def __setitem__(self, key, value):
        # This is only here to avoid pylint errors for the actual attribute field
        raise NotImplementedError

    def dump(self, value):
        return {k: self._contains.dump(v) for k, v in value.items()}

    @property
    def contains(self):
        return self._contains