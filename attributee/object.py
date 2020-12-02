
import inspect

from attributee import Attributee, Attribute, AttributeException

def import_class(classpath):
    delimiter = classpath.rfind(".")
    classname = classpath[delimiter+1:len(classpath)]
    module = __import__(classpath[0:delimiter], globals(), locals(), [classname])
    return getattr(module, classname)

def class_fullname(o):
    return class_string(o.__class__)

def class_string(kls):
    assert inspect.isclass(kls)
    module = kls.__module__
    if module is None or module == str.__class__.__module__:
        return kls.__name__  # Avoid reporting __builtin__
    else:
        return module + '.' + kls.__name__

def default_object_resolver(typename: str, _, **kwargs) -> Attributee:
    """Default object resovler

    Arguments:
        typename {str} -- String representation of a class that can be imported.
            Should be a subclass of Attributee as it is constructed from kwargs.

    Returns:
        Attributee -- An instance of the class
    """
    clstype = import_class(typename)
    assert issubclass(clstype, Attributee)
    return clstype(**kwargs)

class Object(Attribute):

    def __init__(self, resolver=default_object_resolver, subclass=None, **kwargs):
        super().__init__(**kwargs)
        assert subclass is None or inspect.isclass(subclass)
        self._resolver = resolver
        self._subclass = subclass

    def coerce(self, value, context=None):
        assert isinstance(value, dict)
        class_name = value.get("type", None)
        obj = self._resolver(class_name, context, **{k: v for k, v in value.items() if not k == "type"})
        if not self._subclass is None:
            if not isinstance(obj, self._subclass):
                raise AttributeException("Object is not a subclass of {}".format(self._subclass))
        return obj

    def dump(self, value):
        data = value.dump()
        data["type"] = class_fullname(value)
        return data

    def __getattr__(self, name):
        # This is only here to avoid pylint errors for the actual attribute field
        return super().__getattr__(name)

    def __setattr__(self, name, value):
        # This is only here to avoid pylint errors for the actual attribute field
        super().__setattr__(name, value)

    @property
    def subclass(self):
        return self._subclass

class Callable(Attribute):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def coerce(self, value, context=None):
        if callable(value):
            return value

        assert isinstance(value, str)
        caltype = import_class(value)
        assert callable(caltype)
        caltype.resname = value
        return caltype

    def dump(self, value):
        if hasattr(value, "resname"):
            return value.resname
        if inspect.isclass(value):
            return class_string(value)
        return class_fullname(value)

    def __call__(self):
        # This is only here to avoid pylint errors for the actual attribute field
        raise NotImplementedError
