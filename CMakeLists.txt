cmake_minimum_required(VERSION 3.5)
project(ruka_py)

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

# Install Python package
ament_python_install_package(ruka_py)

# Install examples
set(EXAMPLES_DIR examples)
install(PROGRAMS
    ${EXAMPLES_DIR}/ruka_example.py
    DESTINATION lib/${PROJECT_NAME}
)

# Setup the project
ament_package()
