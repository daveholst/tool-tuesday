#!/bin/bash

#build it
poetry build
poetry run pip install --upgrade -t package dist/*.whl
#zip it
cd package ; zip -r ../infra/artifact.zip . -x '*.pyc'
