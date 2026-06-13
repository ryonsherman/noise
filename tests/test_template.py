import os
import tempfile

from noise.template import Template, BOILERPLATE, markdown_filter, markdown_toc


class TestMarkdownFilter:
    def test_converts_basic_markdown(self):
        result = markdown_filter("# Hello")
        assert "<h1" in result
        assert "Hello" in result

    def test_converts_from_file(self):
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False)
        tmp.write("**bold** text")
        tmp.close()
        try:
            result = markdown_filter(tmp.name)
            assert "<strong>bold</strong>" in result
        finally:
            os.unlink(tmp.name)

    def test_fenced_code(self):
        result = markdown_filter("```python\nprint(1)\n```")
        assert "<code" in result
        assert "python" in result


class TestMarkdownToc:
    def test_generates_toc(self):
        result = markdown_toc("# A\n\n## B\n\n### C")
        assert "A" in result
        assert "B" in result

    def test_is_stripped(self):
        result = markdown_toc("# Hello")
        assert result == result.strip()


class TestTemplate:
    def test_renders_string_template(self):
        app = FakeApp()
        tpl = Template(app)
        result = tpl.render("Hello {{ name }}", name="World")
        assert result == "Hello World"

    def test_renders_boilerplate(self):
        app = FakeApp()
        tpl = Template(app)
        result = tpl.render(BOILERPLATE, title="Test", body="Content")
        assert "<title>Test</title>" in result
        assert "Content" in result

    def test_markdown_filter_available(self):
        app = FakeApp()
        tpl = Template(app)
        assert "markdown" in tpl.env.filters


class FakeApp:
    class Path:
        template = "/tmp/nonexistent-template-dir"
    path = Path()
