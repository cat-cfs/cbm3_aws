import unittest
from cbm3_aws.namespace import Namespace


class NamespaceTest(unittest.TestCase):

    def test_namespace_dictionary_round_trip(self):
        data = {
            "a": 1,
            "b": [1, 2],
            "c": {"d": 1, "e": 2},
            "f": {"g": [1, 2], "h": {"i": 1, "j": [2]}}
        }
        ns = Namespace(**data)

        self.assertTrue(ns.a == 1)
        self.assertTrue(ns.b == [1, 2])
        self.assertTrue(ns.c.d == 1)
        self.assertTrue(ns.c.e == 2)
        self.assertTrue(ns.f.g == [1, 2])
        self.assertTrue(ns.f.h.i == 1)
        self.assertTrue(ns.f.h.j == [2])

        data_result = ns.to_dict()
        self.assertTrue(data_result == data)
