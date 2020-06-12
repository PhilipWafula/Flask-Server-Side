#!/usr/bin/env bash

SCRIPT_ABSOLUTE_PATH=$(realpath "$(dirname "${BASH_SOURCE[@]}")")
APP_ABSOLUTE_PATH=$(realpath "$(dirname "$SCRIPT_ABSOLUTE_PATH")")

# export application path to python path
echo "Exporting app path to python path."
export PYTHONPATH=$PYTHONPATH:$APP_ABSOLUTE_PATH
