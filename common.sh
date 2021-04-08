#!/bin/bash
#TPUT
#https://stackoverflow.com/questions/5947742/how-to-change-the-output-color-of-echo-in-linux
#----- Globals -----
repo_path=$(git rev-parse --show-toplevel)

export TERM=xterm-256color

bold=`tput bold`
rev=`tput rev`
thin=`tput sgr0`
red=`tput setaf 1`
green=`tput setaf 2`
yellow=`tput setaf 3`
white=`tput setaf 7`
#-------------------------------------------------------------------------------------------
function exit_on_failure {
    echo " "
    echo "${red}ERROR Spotted${white}"
    echo "${red}-------------------------------------------------------------------------${white}"
    echo "${red}!!! Script: ${BASH_SOURCE[1]}${white}"
    echo "${red}!!! Fatal error in function '${FUNCNAME[1]}' on line ${BASH_LINENO[0]}${white}"
    if [[ ${FUNCNAME[1]} != "main" ]]; then
      echo "${red}!!! Called from function '${FUNCNAME[2]}' on line: ${BASH_LINENO[1]} in ${BASH_SOURCE[2]}${white}"
    fi
    echo "${red}!!! Exiting ...${white}"
    echo "${red}-------------------------------------------------------------------------${white}"
}
#-------------------------------------------------------------------------------------------
# Debug
# Indicates wrong execution, an error
function error_func {
  echo " "
  echo "${bold}${red}!!! Failed Execution of ${yellow}$1${red} !!!${white}${thin}"
  echo " "
  return 1
}
#-------------------------------------------------------------------------------------------
# Exits the script and return 0, indicates successful execution
function success {
  echo " "
  echo "${bold}${green}!!! Succesful Execution of ${yellow}$1${green} !!!${white}${thin}"
  echo " "
  exit 0
}
#-------------------------------------------------------------------------------------------
function display_hint_on_critical_and_exit {
	echo ">>"
	echo ">> Type '$script_name -h' for more information"
	exit 1
}
#-------------------------------------------------------------------------------------------
# Creates the directory for the output files
function storage_dir_create {
  echo "> "
  echo "> Creating Storage Directories"
  master_sim_dir="./generated_files"
  if [[ ! -d $master_sim_dir ]]; then
    echo ">> Created $master_sim_dir"
    mkdir $master_sim_dir
  else
    echo ">> ${green}Already exists: $master_sim_dir${white}"
  fi
}
#-------------------------------------------------------------------------------------------
# Cleans up the directory from files genereted in a previous run
function directory_cleanup {
  echo "> "
	echo "> Removing unneeded files"
	count_log=`ls -1 *.log 2>/dev/null | wc -l`
	count_txt=`ls -1 *.txt 2>/dev/null | wc -l`
	count_wlf=`ls -1 *.wlf 2>/dev/null | wc -l`

	echo ">> .log files for cleaning: ${yellow}$count_log${white}"
	echo ">> .txt files for cleaning: ${yellow}$count_txt${white}"
	echo ">> .wlf files for cleaning: ${yellow}$count_wlf${white}"
	if [ "$count_log" != "0" ]; then
		rm -f *.log
	fi
	if [ "$count_txt" != "0" ]; then
		rm -f *.txt
	fi
	if [ "$count_wlf" != "0" ]; then
		rm -f *.wlf
	fi
	if [ -d ./covhtmlreport ]; then
		rm -r covhtmlreport/
		echo ">> Removed the covhtmlreport directory"
	fi
	echo ">> Cleaned Files: " $(( $count_log + $count_txt + $count_wlf))
}
