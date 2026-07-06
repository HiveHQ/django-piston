"""
Tests for Python 3.12 inspect compatibility changes.

inspect.getargspec() and inspect.formatargspec() were removed in Python 3.12.
These tests verify that getfullargspec() and manual signature formatting
work correctly in decorator.py, doc.py, and emitters.py.
"""

import inspect
import unittest

from piston.decorator import decorator, getinfo, new_wrapper, update_wrapper


class GetinfoTest(unittest.TestCase):
    """Tests for decorator.getinfo using inspect.getfullargspec."""

    def test_simple_function(self):
        def f(x, y):
            pass

        info = getinfo(f)
        self.assertEqual(info["name"], "f")
        self.assertEqual(info["argnames"], ["x", "y"])
        self.assertEqual(info["signature"], "x, y")
        self.assertIsNone(info["defaults"])

    def test_function_with_defaults(self):
        def f(x, y=1, z=2):
            pass

        info = getinfo(f)
        self.assertEqual(info["name"], "f")
        self.assertEqual(info["argnames"], ["x", "y", "z"])
        self.assertEqual(info["defaults"], (1, 2))
        self.assertEqual(info["signature"], "x, y, z")

    def test_function_with_varargs(self):
        def f(x, *args):
            pass

        info = getinfo(f)
        self.assertEqual(info["argnames"], ["x", "args"])
        self.assertEqual(info["signature"], "x, *args")

    def test_function_with_kwargs(self):
        def f(x, **kwargs):
            pass

        info = getinfo(f)
        self.assertEqual(info["argnames"], ["x", "kwargs"])
        self.assertEqual(info["signature"], "x, **kwargs")

    def test_function_with_varargs_and_kwargs(self):
        def f(self, x=1, y=2, *args, **kw):
            pass

        info = getinfo(f)
        self.assertEqual(info["argnames"], ["self", "x", "y", "args", "kw"])
        self.assertEqual(info["defaults"], (1, 2))
        self.assertEqual(info["signature"], "self, x, y, *args, **kw")

    def test_function_with_no_args(self):
        def f():
            pass

        info = getinfo(f)
        self.assertEqual(info["argnames"], [])
        self.assertEqual(info["signature"], "")

    def test_function_docstring(self):
        def f(x):
            """My docstring."""
            pass

        info = getinfo(f)
        self.assertEqual(info["doc"], "My docstring.")

    def test_function_module(self):
        def f(x):
            pass

        info = getinfo(f)
        self.assertEqual(info["module"], __name__)


class UpdateWrapperTest(unittest.TestCase):
    """Tests for decorator.update_wrapper."""

    def test_updates_name_and_doc(self):
        def model(x, y):
            """Model doc."""
            pass

        def wrapper(*args, **kwargs):
            pass

        result = update_wrapper(wrapper, model)
        self.assertEqual(result.__name__, "model")
        self.assertEqual(result.__doc__, "Model doc.")

    def test_updates_defaults(self):
        def model(x, y=5):
            pass

        def wrapper(*args, **kwargs):
            pass

        result = update_wrapper(wrapper, model)
        self.assertEqual(result.__defaults__, (5,))


class NewWrapperTest(unittest.TestCase):
    """Tests for decorator.new_wrapper."""

    def test_preserves_signature(self):
        def model(a, b, c=3):
            """Model function."""
            pass

        def wrapper(*args, **kwargs):
            return args

        result = new_wrapper(wrapper, model)
        self.assertEqual(result.__name__, "model")
        self.assertEqual(result.__doc__, "Model function.")
        # The new wrapper should be callable with the model's signature
        output = result(1, 2, 3)
        self.assertEqual(output, (1, 2, 3))

    def test_from_dict(self):
        infodict = {
            "name": "myfunc",
            "argnames": ["x", "y"],
            "signature": "x, y",
            "defaults": None,
            "doc": "A function.",
            "module": __name__,
            "dict": {},
            "globals": {},
            "closure": None,
        }

        def wrapper(*args, **kwargs):
            return args

        result = new_wrapper(wrapper, infodict)
        self.assertEqual(result.__name__, "myfunc")
        output = result(10, 20)
        self.assertEqual(output, (10, 20))


class DecoratorTest(unittest.TestCase):
    """Tests for the decorator function using getfullargspec."""

    def test_basic_decorator(self):
        @decorator
        def my_decorator(func, *args, **kw):
            return func(*args, **kw)

        @my_decorator
        def add(x, y):
            """Add two numbers."""
            return x + y

        self.assertEqual(add(2, 3), 5)
        self.assertEqual(add.__name__, "add")
        self.assertEqual(add.__doc__, "Add two numbers.")

    def test_decorator_with_default_args(self):
        @decorator
        def my_decorator(func, *args, **kw):
            return func(*args, **kw)

        @my_decorator
        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}!"

        self.assertEqual(greet("World"), "Hello, World!")
        self.assertEqual(greet("World", "Hi"), "Hi, World!")

    def test_decorator_with_varargs(self):
        @decorator
        def my_decorator(func, *args, **kw):
            return func(*args, **kw)

        @my_decorator
        def collect(*args, **kwargs):
            return (args, kwargs)

        self.assertEqual(collect(1, 2, a=3), ((1, 2), {"a": 3}))


try:
    from piston.doc import HandlerMethod

    has_django = True
except (ImportError, ModuleNotFoundError):
    has_django = False


@unittest.skipUnless(has_django, "Django is not installed")
class HandlerMethodIterArgsTest(unittest.TestCase):
    """Tests for doc.HandlerMethod.iter_args using getfullargspec."""

    def test_iter_args_simple(self):
        def read(self, request, pk):
            pass

        method = HandlerMethod(read)
        args = list(method.iter_args())
        self.assertEqual(args, [("pk", None)])

    def test_iter_args_with_defaults(self):
        def read(self, request, pk, format="json"):
            pass

        method = HandlerMethod(read)
        args = list(method.iter_args())
        self.assertEqual(args, [("pk", None), ("format", "json")])

    def test_iter_args_skips_self_request_form(self):
        def create(self, request, form):
            pass

        method = HandlerMethod(create)
        args = list(method.iter_args())
        self.assertEqual(args, [])

    def test_signature_property(self):
        def read(self, request, pk, format=None):
            pass

        method = HandlerMethod(read)
        self.assertEqual(method.signature, "pk, format=<optional>")


class EmittersGetFullArgSpecTest(unittest.TestCase):
    """Tests for emitters.py usage of getfullargspec."""

    def test_getfullargspec_no_args_function(self):
        """Verify getfullargspec works for zero-arg functions (emitters check)."""

        def no_args():
            return 42

        spec = inspect.getfullargspec(no_args)
        self.assertEqual(spec[0], [])
        self.assertEqual(len(spec[0]), 0)

    def test_getfullargspec_one_arg_method(self):
        """Verify getfullargspec works for single-arg methods (emitters check)."""

        class MyModel:
            def emittable(self):
                return "data"

        spec = inspect.getfullargspec(MyModel.emittable)
        self.assertEqual(len(spec[0]), 1)

    def test_getfullargspec_multi_arg_function(self):
        """Verify getfullargspec identifies multi-arg functions correctly."""

        def multi(a, b, c):
            return a + b + c

        spec = inspect.getfullargspec(multi)
        self.assertEqual(len(spec[0]), 3)


if __name__ == "__main__":
    unittest.main()
