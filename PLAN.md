# Noise Modernization Plan

## Goals
- Minimal changes - keep the simplicity
- Port to Python 3.8+
- Fix critical security/compatibility issues
- Add quality-of-life improvements
- Basic test suite
- Updated documentation

---

## Phase 1: Python 3 Port (Core Changes)

### 1.1 Update Python Version Requirements
- Change all shebangs from `#!/usr/bin/env python2` → `#!/usr/bin/env python3`
- Update Makefile commands: `python2` → `python3`, `pip2` → `pip3`, `virtualenv2` → `python3 -m venv`
- Set minimum Python version to 3.8

### 1.2 Fix Python 3 Compatibility Issues
- **map/filter returns**: Wrap `map()` and `filter()` calls with `list()` where needed (path.py:49)
- **Import statements**: Split multi-line imports `import os, sys` → separate lines

### 1.3 Replace Insecure `__import__()`
Current code (line 101 in `__init__.py`):
```python
__import__(args.path).app.build()
```

Replace with safe import using `importlib`:
```python
import importlib.util
spec = importlib.util.spec_from_file_location("project", os.path.join(args.path, "__init__.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.app.build()
```

### 1.4 Fix Markdown Instance Issue
Create new Markdown instance per render instead of global singleton to prevent state leakage.

---

## Phase 2: Modern Packaging

### 2.1 Create `pyproject.toml`
Replace old setup.py pattern with modern packaging:
```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "noise"
version = "2.0.0"
description = "A minimal static website generator"
authors = [{name = "Ryon Sherman", email = "ryon.sherman@gmail.com"}]
license = {text = "MIT"}
requires-python = ">=3.8"
dependencies = [
    "jinja2>=3.0",
    "markdown>=3.3",
]

[project.scripts]
noise = "noise:main"

[project.optional-dependencies]
dev = ["pytest>=7.0", "pytest-cov>=4.0"]
```

### 2.2 Keep setup.py for Compatibility
Keep a minimal setup.py for backward compatibility:
```python
from setuptools import setup
setup()
```

---

## Phase 3: Quality-of-Life Improvements

### 3.1 Better Error Handling
Add try/except blocks for:
- File operations (reading, writing, copying)
- Template rendering
- Module imports
- Invalid paths

### 3.2 Simple Configuration Support
Add optional `noise.toml` config file support:
```toml
[noise]
build_dir = "build"
static_dir = "static"
template_dir = "template"

[markdown]
extensions = ["toc", "abbr", "tables", "fenced_code"]
```

Fall back to current hardcoded defaults if no config file exists.

### 3.3 Basic Logging
Add simple logging to track build process:
- Files being processed
- Routes being rendered
- Errors encountered
- Build completion summary

Use Python's `logging` module with INFO level by default.

### 3.4 Better CLI Output
Improve argparse help text and add:
- `--verbose` flag for detailed output
- `--version` flag to show version
- Better error messages for invalid commands

---

## Phase 4: Testing

### 4.1 Test Structure
Create `tests/` directory with:
- `test_path.py` - Path utilities
- `test_route.py` - Routing system
- `test_template.py` - Template rendering
- `test_page.py` - Page generation
- `test_integration.py` - End-to-end build tests

### 4.2 Test Coverage Goals
- Core functionality: route registration, page rendering, template processing
- Edge cases: invalid paths, missing templates, empty projects
- Python 3 compatibility: ensure map/filter work correctly
- Minimum 70% code coverage

### 4.3 Testing Tools
- pytest for test framework
- pytest-cov for coverage reporting
- Fixtures for temporary test projects

---

## Phase 5: Documentation

### 5.1 Update README.md
Add/update sections:
- **Installation**: Modern pip install instructions
- **Quick Start**: Initialize and build a site
- **Migration from v1**: Breaking changes and how to upgrade
- **Configuration**: Optional noise.toml usage
- **Development**: Running tests, contributing

### 5.2 Migration Guide
Document breaking changes:
- Python 2 → Python 3 requirement
- Command changes (`python2` → `python3`)
- Import mechanism change (no user impact, but mention for transparency)
- Any API changes

### 5.3 Code Documentation
Add docstrings to:
- All classes
- Public methods
- Main functions

Keep it concise - just describe what it does and key parameters.

---

## Phase 6: Cleanup

### 6.1 Update .gitignore
Add modern Python entries:
- `.pytest_cache/`
- `.coverage`
- `.venv/`, `venv/`

### 6.2 Remove Obsolete Files
Consider removing/updating:
- Old-style Makefile (replace with modern alternatives or update for Python 3)
- `src/noise.py` duplicate entry point (consolidate to one)

### 6.3 Update License Year
Update copyright from "2014-2015" to "2014-2026"

---

## Implementation Order

1. **Core Port** (Phase 1) - Get it working with Python 3
2. **Packaging** (Phase 2) - Modern installation
3. **QoL Improvements** (Phase 3) - Better UX
4. **Tests** (Phase 4) - Ensure quality
5. **Documentation** (Phase 5) - Help users
6. **Cleanup** (Phase 6) - Polish

---

## What Stays the Same

- Core architecture and design patterns
- Decorator-based routing API
- Jinja2 + Markdown integration
- Project structure (build/, static/, template/)
- Simple, minimal philosophy
- Existing site projects (with minor updates)
