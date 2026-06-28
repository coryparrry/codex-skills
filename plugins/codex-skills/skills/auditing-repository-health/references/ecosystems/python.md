# Python

## Detection Artifacts

- `pyproject.toml`
- `setup.cfg`
- `setup.py`
- `requirements.txt`
- `tox.ini`
- `noxfile.py`

## Common Repo Shapes

- installable library using `src/<package>` and `tests`
- application package with `requirements.txt` or `pyproject.toml`
- script repo with stdlib-only scripts and focused tests

## Required Lifecycle Gates

- setup: `python -m pip install -e .`, `pip install -r requirements.txt`, `uv sync`, or documented equivalent
- focused test: `pytest`, `python -m unittest`, or documented package-specific command
- full validation: test plus lint/typecheck/build commands when configured

## Native Commands

- `python -m pytest`
- `python -m unittest`
- `python -m py_compile`
- `tox`
- `nox`
- `ruff check`
- `mypy`
- `python -m build`

## CI Expectations

CI should run the same focused or full validation gates documented for local use. Matrix testing is expected when the package claims multiple Python versions.

## Lockfile/Toolchain Policy

Libraries may omit lockfiles for runtime dependencies. Applications should document or commit a lock/sync mechanism such as `uv.lock`, `requirements*.txt`, or a tool-specific lockfile.

## Package Boundary Rules

Do not assume the repo root is the Python package root when `pyproject.toml` appears under a nested directory.

## Common False Positives

- Do not require a server command for libraries or script-only packages.
- Do not require both `tox` and `pytest`.

## Severity Guidance

Missing package-specific tests in a Python package is usually P2. Missing setup instructions in an installable public library is P2 or P1 when it blocks onboarding.

## Good Finding Examples

- P2 scoped to `packages/worker`: `pyproject.toml` declares a Python package, but no local or CI test command references that path.

## Bad Finding Examples

- P2 at root: repo lacks `scripts/test.sh` even though `tox` exists and is documented.
