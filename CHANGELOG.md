# Changelog

All notable changes to this project are documented in this file. The format is
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the
project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-08-25

### Changed

- Removed all built-in joint, link, and planning-group names.
- Added the required `RobotConfig` object so every manipulator declares the
  exact joint order expected by its controller.
- Updated the interactive collision editor to require robot names as command
  line arguments.
- Centralized example-specific names in `examples/robot_config.py`.

### Fixed

- Prevented silent use of an incorrect joint order on manipulators whose URDF
  names differ from the original RUKA setup.

### Migration

Replace `RukaRobot()` with `RukaRobot(RobotConfig(...))`. See the README and
Russian user guide for a complete example.

## [0.1.0] - 2026-08-04

### Added

- High-level `RukaRobot` context-manager API.
- Joint goals and pose goals.
- Joint-space and inverse-kinematics trajectories.
- Collision-object management.
- CSV loading and Euler-to-quaternion conversion.
- Interactive `ruka-collisions` command.
- User examples and automated tests.
- GitHub-ready project metadata, documentation, CI, and contribution guidance.
