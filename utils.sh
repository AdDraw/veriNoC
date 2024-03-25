#!/bin/bash
# AdamDrawc Plumerai@2023

linter_err_file=$GIT_ROOT/linter.err
format_err_file=$GIT_ROOT/format.err
lint_exec=$VERIBLE_BIN/verible-verilog-lint
format_exec=$VERIBLE_BIN/verible-verilog-format
format_exec_default="$format_exec \
                    --verbose=true --verify_convergence=true \
                    --column_limit=120 \
                    --indentation_spaces=2 \
                    --wrap_spaces=2 \
                    --failsafe_success=false \
                    --assignment_statement_alignment=align \
                    --case_items_alignment=align \
                    --class_member_variable_alignment=align \
                    --compact_indexing_and_selections=true \
                    --distribution_items_alignment=align \
                    --enum_assignment_statement_alignment=align \
                    --expand_coverpoints=true \
                    --formal_parameters_alignment=align \
                    --formal_parameters_indentation=wrap \
                    --module_net_variable_alignment=align \
                    --named_parameter_alignment=align \
                    --named_parameter_indentation=wrap \
                    --named_port_alignment=align \
                    --named_port_indentation=indent \
                    --port_declarations_alignment=align \
                    --port_declarations_indentation=wrap \
                    --port_declarations_right_align_packed_dimensions=true \
                    --port_declarations_right_align_unpacked_dimensions=true \
                    --struct_union_members_alignment=align \
                    --try_wrap_long_lines=true"

check_lint() {
  # Lints a single file according to rules set in $GIT_ROOT/scripts/verible/verible_verilog_lint_rules.txt
  # lint result is dumped to linter.err file
  # returns a 0/1 depending on linter status
  echo "INFO> checking lint: $1..."
  $lint_exec --rules_config $GIT_ROOT/../verible-linter-action/lint_rules.txt \
             --show_diagnostic_context=true \
             $1 &> tmp.log
  ec=$?

  if [[ -s tmp.log ]]; then
    cat tmp.log >> $linter_err_file
  fi
  rm tmp.log
  return $ec
}

check_format () {
  # Checks formatting of a single file
  # format check is not supported by verible by default thus
  # file is formatted and the result of the format is dumped to a tmp file
  # tmp file is diffed against file in repo
  # if diff size is bigger than 0 then there is a mismatch in formatting
  # formatting rules are set in $format_exec_default above
  # format_err_file holds diffs
  echo "INFO> checking format: $1..."

  $format_exec_default $1 &> tmp.log

  diff tmp.log $1 > diff.log || : # don't return an errror
  if [[ -s diff.log ]] ; then
    echo "WARN > differences found in $1"
    rm tmp.log
    echo "" >> $format_err_file
    echo "$1:" >> $format_err_file
    cat diff.log >> $format_err_file
    rm diff.log
    return 1
  fi
  return 0
}

format () {
  # Takes a list of space separeted files(paths to files)
  # and formats them according to $format_exec_default flags
  echo "INFO> Formatting files..."
  $format_exec_default --inplace $*
  return $?
}