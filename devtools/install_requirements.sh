#!/bin/bash

# install requirements
cd ../app || exit
pip3 install -r requirements.txt

cd ../tests || exit
pip3 install -r requirements.txt

# return to parent directory
cd ../
