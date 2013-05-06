#!/bin/bash
# compass/compass.sh - properly invoke the "Compass" program

BASE=$PWD
export GEM_HOME=$BASE/Gem
export RUBYLIB=$BASE/Gem/lib
$BASE/Gem/bin/compass "$@"
