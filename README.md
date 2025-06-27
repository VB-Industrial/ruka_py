# ruka_py
python bindings for moveit2 ruka package

```bash
# Clone this repository into your favourite ROS 2 workspace
git clone https://github.com/VB-Industrial/ruka_py.git
# Install dependencies
rosdep install -y -r -i --rosdistro ${ROS_DISTRO} --from-paths .
# Build
colcon build --merge-install --symlink-install --cmake-args "-DCMAKE_BUILD_TYPE=Release"
```

### Sourcing

Before utilising this package, remember to source the ROS 2 workspace.

```bash
source install/local_setup.bash
```
