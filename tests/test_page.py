import os
import shutil
import tempfile

from noise.page import Page
from noise.route import format_route


class FakeApp:
    def __init__(self):
        self.template = FakeTemplate()

    class Path:
        def __init__(self, base):
            self.base = base
            self.build = PathHelper(base)
            self.template = PathHelper(base)

        def __call__(self, *parts):
            return os.path.join(self.base, *parts)

    path = None


class PathHelper:
    def __init__(self, base):
        self.base = base

    def __call__(self, path):
        return os.path.join(self.base, path.lstrip("/"))

    def relative(self, path):
        return "/" + os.path.relpath(str(path), self.base)


class FakeTemplate:
    def render(self, template, **data):
        return "rendered: {} | {}".format(template, data)


class TestPage:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_page_initializes(self):
        app = self._make_app()
        page = Page(app, "/foo")
        assert page.route == "/foo.html"
        assert page.path.endswith("/foo")

    def test_render_disabled_when_template_none(self):
        app = self._make_app()
        page = Page(app, "/foo", template=None)
        page.render()
        assert page.rendered is True

    def test_render_writes_output(self):
        app = self._make_app()
        page = Page(app, "/bar")
        page.render()
        assert os.path.exists(page.path)
        with open(page.path) as f:
            content = f.read()
        assert "rendered:" in content

    def _make_app(self):
        app = FakeApp()
        app.path = FakeApp.Path(self.tmpdir)
        os.makedirs(os.path.join(self.tmpdir, "build"))
        return app
