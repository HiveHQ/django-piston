"""
Tests verifying Python 3.12 + Django 4.2 compatibility fixes.
Run with: python -m pytest tests/test_python312_compat.py
"""

import os
import sys

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.test_project.settings")

# Add test_project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()


class TestDecoratorModule:
    """Tests for piston/decorator.py fixes (getargspec/formatargspec removal)."""

    def test_getinfo_simple_function(self):
        from piston.decorator import getinfo

        def sample(self, x, y=1):
            pass

        info = getinfo(sample)
        assert info["name"] == "sample"
        assert info["argnames"] == ["self", "x", "y"]
        assert "self" in info["signature"]
        assert "x" in info["signature"]
        assert "y" in info["signature"]
        assert info["defaults"] == (1,)

    def test_getinfo_with_varargs_and_kwargs(self):
        from piston.decorator import getinfo

        def sample(a, b, *args, **kwargs):
            pass

        info = getinfo(sample)
        assert info["name"] == "sample"
        assert "args" in info["argnames"]
        assert "kwargs" in info["argnames"]
        assert "*args" in info["signature"]
        assert "**kwargs" in info["signature"]

    def test_decorator_works(self):
        from piston.decorator import decorator

        @decorator
        def my_decorator(func, *args, **kwargs):
            return func(*args, **kwargs)

        @my_decorator
        def hello(name):
            return f"hello {name}"

        assert hello("world") == "hello world"
        assert hello.__name__ == "hello"


class TestEmittersModule:
    """Tests for piston/emitters.py fixes (urlresolvers, permalink, getargspec)."""

    def test_emitter_import(self):
        from piston.emitters import Emitter, JSONEmitter

        assert Emitter is not None
        assert JSONEmitter is not None

    def test_reverser_function(self):
        from piston.emitters import reverser

        # reverser should be callable and return a function
        assert callable(reverser)


class TestUtilsModule:
    """Tests for piston/utils.py fixes (ugettext removal)."""

    def test_utils_import(self):
        from piston.utils import HttpStatusCode, Mimer

        assert HttpStatusCode is not None
        assert Mimer is not None


class TestDocModule:
    """Tests for piston/doc.py fixes (render_to_response, getargspec)."""

    def test_handler_documentation_import(self):
        from piston.doc import HandlerDocumentation

        assert HandlerDocumentation is not None

    def test_handler_documentation_iter_args(self):
        from piston.doc import HandlerMethod

        def sample_method(self, request, pk=None):
            pass

        hm = HandlerMethod(sample_method)
        # Should not raise AttributeError for getargspec
        args = list(hm.iter_args())
        # 'self' and 'request' are filtered out, only 'pk' remains
        assert len(args) == 1
        assert args[0][0] == "pk"


class TestAuthenticationModule:
    """Tests for piston/authentication.py fixes."""

    def test_authentication_import(self):
        from piston.authentication import HttpBasicAuthentication

        assert HttpBasicAuthentication is not None


class TestModels:
    """Tests for piston/models.py fixes (ForeignKey on_delete)."""

    def test_consumer_model_import(self):
        from piston.models import Consumer

        # Verify ForeignKey fields have on_delete set
        user_field = Consumer._meta.get_field("user")
        assert user_field.remote_field.on_delete is not None
