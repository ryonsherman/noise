import os
import shutil
import sys
import tempfile

import pytest


@pytest.fixture
def project_dir():
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    shutil.rmtree(tmpdir, ignore_errors=True)


def test_init_creates_project(project_dir):
    from noise import Noise
    n = Noise(project_dir)
    n.init()
    assert os.path.exists(os.path.join(project_dir, "__init__.py"))
    assert os.path.exists(os.path.join(project_dir, "build"))
    assert os.path.exists(os.path.join(project_dir, "static"))
    assert os.path.exists(os.path.join(project_dir, "template"))


def test_build_creates_output(project_dir):
    from noise import Noise
    n = Noise(project_dir)
    n.init()

    @n.route("/")
    def index(page):
        page.data["title"] = "Test"
        page.data["body"] = "Hello"

    n.build()
    index_path = os.path.join(project_dir, "build", "index.html")
    assert os.path.exists(index_path)
    with open(index_path) as f:
        content = f.read()
    assert "<title>Test</title>" in content
    assert "Hello" in content


def test_multiple_routes(project_dir):
    from noise import Noise
    n = Noise(project_dir)
    n.init()

    @n.route("/")
    def index(page):
        page.data["title"] = "Home"
        page.data["body"] = "Welcome"

    @n.route("/about")
    def about(page):
        page.data["title"] = "About"
        page.data["body"] = "About us"

    n.build()
    assert os.path.exists(os.path.join(project_dir, "build", "index.html"))
    assert os.path.exists(os.path.join(project_dir, "build", "about.html"))


def test_static_files_copied(project_dir):
    from noise import Noise
    n = Noise(project_dir)
    n.init()

    os.makedirs(os.path.join(project_dir, "static", "css"))
    with open(os.path.join(project_dir, "static", "css", "style.css"), "w") as f:
        f.write("body { color: red; }")

    n.build()
    assert os.path.exists(os.path.join(project_dir, "build", "css", "style.css"))
