# ruka_py

`ruka_py` is a high-level Python interface for controlling the six-axis RUKA
manipulator with ROS 2, MoveIt 2, and `pymoveit2`.

The library owns the repetitive infrastructure—ROS initialization, the node,
background executor, MoveIt client, trajectory messages, and cleanup—so user
programs contain only motion commands and trajectory data.

> **Project status:** alpha. Validate every motion in simulation before using
> this package with physical hardware.

## Features

- joint-space and pose goals;
- joint-space trajectories with fractional timestamps;
- pose trajectories with inverse kinematics;
- CSV trajectory loading;
- Euler-angle to quaternion conversion;
- box, sphere, cylinder, and cone collision objects;
- deterministic ROS cleanup through a context manager;
- type information for IDEs and static analyzers.

## Requirements

- Linux;
- Python 3.10 or newer;
- ROS 2 with `rclpy`, `builtin_interfaces`, and `trajectory_msgs`;
- MoveIt 2;
- [`pymoveit2`](https://github.com/AndrejOrsula/pymoveit2);
- a running RUKA driver or simulation with MoveIt and controllers configured.

The default configuration targets ROS 2 Jazzy and `pymoveit2` 4.x. Other ROS 2
distributions may work but are not currently tested in CI.

## Installation

Source ROS 2 and the workspace containing `pymoveit2`:

```bash
source /opt/ros/jazzy/setup.bash
source ~/ws_ruka/install/setup.bash
```

Using a virtual environment with access to ROS system packages is recommended:

```bash
sudo apt install python3-venv
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
```

Install from a local clone:

```bash
git clone https://github.com/VB-Industrial/ruka_py.git
cd ruka_py
python3 -m pip install .
```

After the repository has a tagged release, it can also be installed directly:

```bash
python3 -m pip install \
  "ruka_py @ git+https://github.com/VB-Industrial/ruka_py.git@v0.1.0"
```

## Quick start

```python
from ruka_py import RukaRobot, euler_deg_to_quaternion


with RukaRobot(max_velocity=0.5, max_acceleration=0.3) as robot:
    robot.move_to_angles([0.0, -1.57, 1.57, 0.0, 0.0, 0.0])

    orientation = euler_deg_to_quaternion(0, 0, 0)
    robot.move_to_pose([0.256, 0.0, 0.5628], orientation)
```

Always use `RukaRobot` as a context manager. This ensures that the executor,
node, and ROS context are released if the program finishes or raises an error.

## Examples

The [`examples`](examples) directory contains runnable scenarios:

- [`move_by_angles.py`](examples/move_by_angles.py);
- [`move_to_pose.py`](examples/move_to_pose.py);
- [`trajectory_from_csv.py`](examples/trajectory_from_csv.py);
- [`pose_trajectory.py`](examples/pose_trajectory.py).

Run an example only after starting the robot or simulation and sourcing ROS:

```bash
python3 examples/move_by_angles.py
```

The collision-object editor is installed as a command-line application:

```bash
ruka-collisions
```

## Documentation

The complete Russian-language user guide is available in
[`docs/usage_ru.md`](docs/usage_ru.md). It documents trajectories, CSV files,
collision objects, custom robot configuration, and common errors.

## Development

Install development dependencies and run the checks:

```bash
python3 -m pip install -e ".[dev]"
python3 -m ruff check ruka_py examples tests
python3 -m pytest
python3 -m pip wheel . --no-deps --wheel-dir dist
```

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the contribution and release
workflow. GitHub Actions runs tests and builds a wheel for every push and pull
request.

## Safety

This software can command physical machinery. The authors provide no guarantee
that a trajectory is collision-free or safe for a particular installation.
Test in simulation, start with reduced velocity and acceleration, keep an
emergency stop available, and follow the safety procedures for your robot.

## License

Licensed under the Apache License 2.0. See [`LICENSE`](LICENSE).
