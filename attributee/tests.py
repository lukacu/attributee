
import unittest

from attributee import AttributeException, Attributee, Include, Nested, Unclaimed
from attributee.containers import List, Map
from attributee.primitives import Integer

class Tests(unittest.TestCase):

    def test_nested(self):
        
        class A(Attributee):

            a = Integer()
            b = Integer()

        class B(Attributee):

            nested = Nested(A)
            c = Integer()

        b = B(nested=dict(a=1, b=2), c=3)

        self.assertEqual(getattr(b, "c", 0), 3)
        self.assertEqual(getattr(b.nested, "a", 0), 1)
        self.assertEqual(getattr(b.nested, "b", 0), 2)

    def test_include(self):
        
        class A(Attributee):

            a = Integer()
            b = Integer()

        class B(Attributee):

            inner = Include(A)
            c = Integer()

        b = B(a=1, b=2, c=3)

        self.assertEqual(getattr(b, "c", 0), 3)
        self.assertEqual(getattr(b.inner, "a", 0), 1)
        self.assertEqual(getattr(b.inner, "b", 0), 2)

    def test_unclaimed(self):
        
        class A(Attributee):

            a = Integer()
            b = Integer()

            rest = Unclaimed()

        a = A(a=1, b=2, c=3, d=4)

        self.assertEqual(getattr(a, "a", 0), 1)
        self.assertEqual(getattr(a, "b", 0), 2)
        self.assertEqual(a.rest.get("c", 0), 3 )
        self.assertEqual(a.rest.get("d", 0), 4 )

    def test_readonly(self):
        
        class A(Attributee):
            a = Integer(readonly=True)
            b = Integer(readonly=False)

        a = A(a=2, b=2)

        def set_readonly(v):
            a.a = v

        self.assertRaises(AttributeException, set_readonly, 1)
        self.assertEqual(a.a, 2)

        try:
            a.b = 1
            self.assertEqual(a.b, 1)
        except AttributeException:
            self.fail()

    def test_readonly_containers(self):
        
        class A(Attributee):
            ro_list = List(Integer(), readonly=True)
            ro_map = Map(Integer(), readonly=True)

            rw_list = List(Integer(), readonly=False)
            rw_map = Map(Integer(), readonly=False)


        a = A(ro_list=[1], ro_map={"a": 1}, rw_list=[1], rw_map={"a": 1})

        def append_readonly(v):
            a.ro_list.append(v)

        def set_readonly(k, v):
            a.ro_map[k] = v

        self.assertRaises(AttributeException, append_readonly, 1)
        self.assertEqual(len(a.ro_list), 1)


        self.assertRaises(AttributeException, set_readonly, "a", 2)
        self.assertRaises(AttributeException, set_readonly, "b", 1)
        self.assertEqual(len(a.ro_map), 1)

        try:
            a.rw_list.append(1)
            self.assertEqual(len(a.rw_list), 2)
        except AttributeException:
            self.fail()

        try:
            a.rw_map["a"] = 2
            a.rw_map["b"] = 1
            self.assertEqual(a.rw_map["a"], 2)
            self.assertEqual(a.rw_map["b"], 1)
        except AttributeException:
            self.fail()