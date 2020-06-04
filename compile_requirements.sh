#!/usr/bin/env bash

export CUSTOM_COMPILE_COMMAND='./compile_requirements.sh'

pip-compile --no-index requirements/requirements.in $1 $2 $3
pip-compile --no-index requirements/test-requirements.in $1 $2 $3
