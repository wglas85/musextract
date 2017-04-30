#!/bin/sh
#
# Clean the project
#

cd $(dirname $0)

test -d dist && rm -rf dist
test -d build && rm -rf build
test -d doc/build && rm -rf doc/build
test -d musextract.egg-info && rm -rf musextract.egg-info
test -d .pybuild && rm -rf .pybuild
test -d src/musextract.egg-info && rm -rf src/musextract.egg-info
for file in $(find . -name __pycache__ ); do rm -rf $file; done
for file in $(find . -type f -name '*.log' ); do rm -f $file; done
for file in $(find . -type f -name '*~' ); do rm -f $file; done
exit 0
