# Contributing

Thank you for contributing to `ruka_py`.

## Development setup

1. Install ROS 2 Jazzy, MoveIt 2, and `pymoveit2`.
2. Source ROS and the workspace containing `pymoveit2`.
3. Create a virtual environment that can access ROS system packages.
4. Install the project with development dependencies.

```bash
source /opt/ros/jazzy/setup.bash
source ~/ws_ruka/install/setup.bash
sudo apt install python3-venv
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
python3 -m pip install -e ".[dev]"
```

## Before opening a pull request

Run all local checks:

```bash
python3 -m ruff check ruka_py examples tests
python3 -m pytest
python3 -m pip wheel . --no-deps --wheel-dir dist
```

Keep changes focused, add tests for changed behavior, and update the README or
user guide when the public API changes. Do not include generated files such as
`build`, `dist`, `*.egg-info`, or `__pycache__`.

## Commit and pull-request guidance

- Use imperative, descriptive commit messages.
- Explain the problem and the chosen solution in the pull request.
- State whether the change was tested in simulation, on hardware, or only with
  automated tests.
- Call out any compatibility or safety implications.

## Release checklist

1. Ensure CI is green.
2. Update `CHANGELOG.md` and remove changes from the Unreleased section.
3. Update the version in `pyproject.toml` and `ruka_py/__init__.py`.
4. Build and inspect the wheel.
5. Create an annotated Git tag such as `v0.2.0`.
6. Create a GitHub release from that tag.
