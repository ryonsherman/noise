install:
	pip3 install -e .

uninstall:
	pip3 uninstall noise -y

dep:
	pip3 install jinja2 markdown

dev:
	python3 -m venv dev
	@echo ""
	@echo "Run 'source dev/bin/activate' to enable the virtual environment."
	@echo "Run 'deactivate' once complete."
	@echo ""
	@echo "To install dependencies, run 'make dep'."
	@echo "To install, run 'make install' or 'pip3 install -e .'"

clean:
	rm -rf dev build dist *.egg-info __pycache__ .pytest_cache
	rm -rf src/noise/__pycache__

test:
	python3 -m pytest tests/ -v
