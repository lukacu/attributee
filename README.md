Attributee
----------

[![PyPI package version](https://badge.fury.io/py/attributee.svg)](https://badge.fury.io/py/attributee)
[![CI](https://github.com/lukacu/attributee/actions/workflows/ci.yml/badge.svg)](https://github.com/lukacu/attributee/actions/workflows/ci.yml)

Attributee is a Python library for declarative object initialization. Input
arguments are defined as class attributes and automatically processed when an
object is created. It is useful for small configuration and data-model classes
where validation, defaults, and nested values should be declared alongside the
class definition.

The library is deliberately small and evolves around practical configuration
and data-modeling needs.

Installation
============

Install the latest release from PyPI:

```
python -m pip install attributee
```

Simple use case
===============

```
from attributee import Attributee, String, Float

class Model(Attributee):

    # Simply list the attributes of the object ...

    name = String(default="noname")
    value1 = Float()
    value2 = Float(default=0, val_min=-10, val_max=10)

    # ... no constructor needed


# default arguments assigned
model1 = Model(value1=10)

# automatic type conversion where possible
model2 = Model(value1=10, value2="5")

```

Declared attributes can provide defaults, type conversion, validation, and
read-only behavior. The package also includes nested models, containers,
serialization helpers, and additional primitive types.

Supported Python versions
=========================

Attributee supports Python 3.6 and newer. Continuous integration currently
tests Python 3.9 through 3.12.

Development
===========

Run the test suite from a checkout with:

```
python -m unittest attributee.tests -v
```

Build distributions locally with:

```
python -m pip install build
python -m build
```

Documentation
=============

I am working on it.

Authors
=======

Luka Čehovin Zajc

License
=======

The library is available under the [simplified BSD license](LICENSE.md).
