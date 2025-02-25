# Owner(s): ["module: inductor"]
import operator
import os

from torch._inductor.compile_worker.subproc_pool import (
    raise_testexc,
    SubprocPool,
    TestException,
)

from torch._inductor.test_case import TestCase
from torch.testing._internal.inductor_utils import HAS_CPU


class TestCompileWorker(TestCase):
    def test_basic_jobs(self):
        pool = SubprocPool(2)
        try:
            a = pool.submit(operator.add, 100, 1)
            b = pool.submit(operator.sub, 100, 1)
            self.assertEqual(a.result(), 101)
            self.assertEqual(b.result(), 99)
        finally:
            pool.shutdown()

    def test_exception(self):
        pool = SubprocPool(2)
        try:
            a = pool.submit(raise_testexc)
            with self.assertRaises(TestException):
                a.result()
        finally:
            pool.shutdown()

    def test_crash(self):
        pool = SubprocPool(2)
        try:
            with self.assertRaises(Exception):
                a = pool.submit(os._exit, 1)
                a.result()

            # Pool should still be usable after a crash
            b = pool.submit(operator.add, 100, 1)
            c = pool.submit(operator.sub, 100, 1)
            self.assertEqual(b.result(), 101)
            self.assertEqual(c.result(), 99)
        finally:
            pool.shutdown()


if __name__ == "__main__":
    from torch._inductor.test_case import run_tests

    if HAS_CPU:
        run_tests()
