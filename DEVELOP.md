# Development quick start

We recommend using [uv](https://github.com/astral-sh/uv) for development tasks.

We use `mypy` in strict mode for type checking, `pytest` for testing,
and `ruff` for linting and formatting.

From the root directory of the repository:

- Run `uv run mypy` to check types.
- Run `uv run pytest` to execute the test suite.
- Run `uv run coverage run` to execute the test suite under coverage.
- Run `uvx ruff check` for linting checks.
- Run `uvx ruff format` to format the code.
