from noise.route import format_route, Route, BOILERPLATE


class TestFormatRoute:
    def test_prepends_slash(self):
        assert format_route("foo") == "/foo.html"

    def test_keeps_existing_slash(self):
        assert format_route("/foo") == "/foo.html"

    def test_appends_index_for_trailing_slash(self):
        assert format_route("/") == "/index.html"

    def test_keeps_existing_extension(self):
        assert format_route("/foo.xml") == "/foo.xml"

    def test_handles_nested_path(self):
        assert format_route("/foo/bar") == "/foo/bar.html"


class TestRoute:
    def test_registers_route(self):
        app = FakeApp()
        route = Route(app)

        @route("/foo")
        def handler(page):
            pass

        assert app.routes["/foo.html"] is handler

    def test_returns_callback(self):
        app = FakeApp()
        route = Route(app)

        def handler(page):
            pass

        result = route("/foo")(handler)
        assert result is handler


class TestBoilerplate:
    def test_is_string(self):
        assert isinstance(BOILERPLATE, str)

    def test_contains_python3(self):
        assert "python3" in BOILERPLATE

    def test_contains_noise_import(self):
        assert "from noise import Noise" in BOILERPLATE


class FakeApp:
    def __init__(self):
        self.routes = {}
