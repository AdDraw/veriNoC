#!/bin/bash
set -eE
trap 'exit_on_failure' ERR

repo_path=$(git rev-parse --show-toplevel)

source $repo_path/common.sh
path2jsons=$repo_path/synth/json_files
path2logs=$repo_path/synth/logs
export "JSON_PATH=$path2jsons"
export "LOG_PATH=$path2logs"
echo "$(pwd)"
script_name=$BASH_SOURCE

#-------------------------------------------------------------------------------------------
function display_help {
  echo "${bold}>> $script_name manual:"
  echo ">> NAME"
  echo ">>            $script_name - runs synthesis with YOSYS and passes PARAMETERs"
  echo ">> "
  echo ">> SYNOPSIS"
  echo ">>            ./yosys_wrapper.sh -sf [ -show-params ] [--no-xdot] [ -h ] [ PARAMETERs ]"
  echo ">> "
  echo ">> DESCRIPTION"
  echo ">>            Acts as a wrapper for the yosys suite"
  echo ">> "
  echo ">> OPTIONS"
  echo ">>            -sf/--script-file - tcl script that contains yosys commands"
  echo ">>"
  echo ">>            --show-params     - presents the parameters of the top module only (no synthesis)"
  echo ">>"
  echo ">>            --xdot            - enables yosys show command"
  echo ">>"
  echo ">>            --std-lib         - path to std cell library, default: std_libs/osu018_std.lib"
  echo ">>"
  echo ">>            -h/--help         - by using a help switch this manual will be seen"
	echo ">>"
  echo ">>            PARAMETERs       - Design parameter values passed as POSITIONAL values"
  echo ">>                               PARAM=VALUE(for ex. ROW_N=3)"
  echo ">> "
  echo ">> ADDITIONAL"
  echo ">>       All the other arguments are ignored when you add the -h option${thin}"
	exit 0
}

# Create and check if directories are created
if [[ ! -d $path2logs ]]; then
  mkdir "$path2logs"
fi

if [[ ! -d $path2jsons ]]; then
  mkdir "$path2jsons"
fi

POSITIONAL=() # list that should store parameters as positional arguments
TCL_FILE="null"
STD_LIB="std_libs/osu18_std.lib"
export SHOW_PARAMS=0
while [[ $# -gt 0 ]]
do
  key="$1"
  case $key in
      -sf|--script-file)
      SCRIPT_FILE="$2"
      shift # past argument
      shift # past value
      ;;
      --show-params)
      echo "${green}Setting SHOW_PARAMS=1${white}"
      export SHOW_PARAMS=1
      shift # past argument
      ;;
      --xdot)
      echo "${green}Setting XDOT=1${white}"
      export XDOT=1
      shift # past argument
      ;;
      --std-lib)
      echo "${green}Setting STD_LIB="$2"${white}"
      STD_LIB="$2"
      shift # past argument
      shift
      ;;
      -h|--help)
      display_help
      ;;
      *)    # unknown option
      POSITIONAL+=("$1") # save it in an array for later
      shift
      ;;
  esac
done
export STD_LIB=$STD_LIB
# Check if the script was passed
if [[ $SCRIPT_FILE == "null" ]]; then
  #statements
  echo "${red}ERROR: TCL script was not passed!${white}"
  error_func $script_name
fi

# For every PARAMETER that was passed SET EXPORT it
# so that they its visible from inside YOSYS
for param in "${POSITIONAL[@]}";
do
  echo "${green}Setting ENVVAR: "$param" "${white}
  export "${param?}" || error_func "$script_name"
done

# SCRIPT_FILE parsing (remove .tcl from the file name)
script_file_edit=${SCRIPT_FILE%".tcl"}
synth_log_name=$path2logs/$script_file_edit".log"

yosys -tl "$synth_log_name" "$SCRIPT_FILE" || error_func "$script_name"

if [[ -e ~/.yosys_show.dot ]]; then
  #statements
  if [[ ! -d $repo_path/synth/dot_files ]]; then
    #statements
    mkdir "$repo_path/synth/dot_files"
  fi
  cp ~/.yosys_show.dot "$repo_path/synth/dot_files/.$script_file_edit.dot"
fi

success "$script_name"