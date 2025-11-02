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

## Making a release

There's a GitHub Actions workflow that will automatically publish a release to
PyPI when a GitHub release is created.

Steps to make a release:

- Bump the version number in the `pyproject.toml` file if necessary, for example using
  `uv version --bump minor` for a minor release. (Note: this also updates the lockfile.)
  Make a PR for the version bump.
- Ensure that the lockfile has been updated. (Not necessary if you used `uv version`.)
- Prepare release notes in a (temporary) markdown file.
- Tag the release commit with an annotated tag matching the version:

      git tag -a $(uv version --short)

  Include the prepared release notes in the commit message body.
- Push the tag with `git push --tag`
- Go to the GitHub releases page: https://github.com/mdickinson/simplefractions/releases
- Create a new release ("Draft a new release"), using the previously-prepared release
  notes and a release title of the form "simplefractions n.n.n".
- Double-check that the release workflow succeeded and that the new release is present
  on PyPI at https://pypi.org/project/simplefractions.
