#!/bin/bash
set -e

GIT_ROOT=$(git rev-parse --show-toplevel)
VERIBLE_DIR=$GIT_ROOT
# source "$GIT_ROOT/scripts/env.sh"
VERIBLE_BIN=/opt/verible-v0.0-2479-g92928558/bin/
source $VERIBLE_DIR/utils.sh
v_files=$(find $GIT_ROOT -name *.*v )
format $v_files
exit $?
