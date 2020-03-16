#!/bin/bash

# install requirements
cd app || exit
pip install - requirements.txt

# return to parent directory
cd ..

# export path to python path
ABSOLUTE_PATH_FOR_SCRIPT=$(realpath "$(dirname "${BASH_SOURCE[@]}")")
export PYTHONPATH=$PYTHONPATH:$ABSOLUTE_PATH_FOR_SCRIPT/app