run-tests:
	uv run python -m unittest discover -s . -v
run:
	uv run main.py