#!/bin/bash
path2json=$(pwd)/json_files
path2log=$(pwd)/logs

if [[ ! -d logs ]]; then
  mkdir logs
fi

if [[ ! -d json_files ]]; then
  mkdir json_files
fi

export "JSON_PATH=$path2json"
export "LOG_PATH=$path2log"

POSITIONAL=()
while [[ $# -gt 0 ]]
do
  key="$1"
  case $key in
      -sf|--script_file)
      SCRIPT_FILE="$2"
      shift # past argument
      shift # past value
      ;;
      *)    # unknown option
      POSITIONAL+=("$1") # save it in an array for later
      shift
      ;;
  esac
done

# For every PARAMETER SET EXPORT it so that they its visible from inside YOSYS
echo "PARAMETERS set:"
for param in ${POSITIONAL[@]};
do
  echo $param
  export $param
done

script_file_edit=${SCRIPT_FILE%".tcl"}
#SCRIPT_FILE parsing (remove .tcl from the file name)
synth_log_name=$path2log/$script_file_edit".log"

yosys -tl $synth_log_name $SCRIPT_FILE


if [[ -e ~/.yosys_show.dot ]]; then
  #statements

  if [[ ! -d dot_files ]]; then
    #statements
    mkdir dot_files
  fi
  cp ~/.yosys_show.dot ./dot_files/.$script_file_edit.dot
fi
