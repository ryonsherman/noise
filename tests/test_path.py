import os
import tempfile

from noise.path import NoisePath, Path


class TestNoisePath:
    def test_normalizes_path(self):
        p = NoisePath("/foo/bar/../baz")
        assert str(p) == "/foo/baz"

    def test_strips_filename(self):
        p = NoisePath("/foo/bar/file.txt")
        assert str(p) == "/foo/bar"

    def test_call_joins_path(self):
        p = NoisePath("/foo")
        assert p("bar") == "/foo/bar"
        assert p("/bar") == "/foo/bar"

    def test_relative_helper(self):
        p = NoisePath("/foo/bar")
        rel = p.relative("/foo/bar/baz/qux")
        assert rel == "/baz/qux"

    def test_relative_root(self):
        p = NoisePath("/foo")
        assert str(p.relative) == "/"


class TestPath:
    def test_creates_sub_paths(self):
        p = Path("/tmp/noise-test-path")
        assert hasattr(p, "build")
        assert hasattr(p, "static")
        assert hasattr(p, "template")

    def test_init_creates_directories(self):
        path = os.path.join(tempfile.gettempdir(), "noise-test-init")
        p = Path(path)
        p.init()
        try:
            assert os.path.exists(path)
            assert os.path.exists(p.build.path)
            assert os.path.exists(p.static.path)
            assert os.path.exists(p.template.path)
        finally:
            import shutil
            shutil.rmtree(path, ignore_errors=True)

    def test_init_is_idempotent(self):
        path = os.path.join(tempfile.gettempdir(), "noise-test-init2")
        p = Path(path)
        p.init()
        p.init()
        try:
            assert os.path.exists(path)
        finally:
            import shutil
            shutil.rmtree(path, ignore_errors=True)
