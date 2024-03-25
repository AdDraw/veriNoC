#!/usr/bin/env bash
# set -e


GIT_ROOT=$(git rev-parse --show-toplevel)
VERIBLE_DIR=$GIT_ROOT
VERIBLE_BIN=/opt/verible-v0.0-2479-g92928558/bin/

# source "$GIT_ROOT/scripts/env.sh"
source $VERIBLE_DIR/utils.sh


### MAIN
v_files=$(find $GIT_ROOT -name *.v)

if [[ -f "$linter_err_file" ]]; then
  echo "INFO> Found old linter.err file, removing..."
  rm $linter_err_file
fi

if [[ -f "$format_err_file" ]]; then
  echo "INFO> Found old format.err file, removing..."
  rm $format_err_file
fi

# Linter & Formatter checks
linter_err_cnt=0
format_err_cnt=0
for f in $v_files
do
  check_lint $f || linter_err_cnt=$(( $linter_err_cnt + $?))
  check_format $f || format_err_cnt=$(( $format_err_cnt + $?))
done

echo ""
echo "INFO> Summary:"

if [[ $linter_err_cnt -gt 0 ]]; then
  echo "ERROR> $linter_err_cnt files did not pass lint check..., details at $linter_err_file"
  if [[ $show_lint_file -eq 1 ]]; then
    cat $linter_err_file
  fi
else
  echo "INFO> LINT SUCCESS!"
fi

if [[ $format_err_cnt -gt 0 ]]; then
  echo "ERROR> $format_err_cnt files did not pass format check..., details at $format_err_file"
  if [[ $show_format_file -eq 1 ]]; then
    cat $format_err_file
  fi
else
  echo "INFO> FORMAT SUCCESS!"
fi

exit $(( $linter_err_cnt + $format_err_cnt ))