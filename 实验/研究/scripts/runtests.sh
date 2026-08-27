#!/bin/bash
# Wrapper to run pytest with ROS2 plugin autoload disabled
# Reason: ROS2 launch_pytest/launch_testing packages require 'lark' module
# which is not installed in this project environment. Disabling plugin
# autoload prevents import errors during test collection.

export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m pytest "$@"
