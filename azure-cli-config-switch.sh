#!/bin/bash

# USAGE: place all kube configuration directories under the directory set by AZURE_CONFIGS
#        then, use any of the commands:
#        caz <config-name> - to use the config by that name from the AZURE_CONFIGS
AZURE_CONFIGS=${HOME}/.azureconfigs

function caz() {
  if [ -z "$1" ]; then
    export AZURE_CONFIG_DIR=""
    return 0;
  fi

  local chosen_dir=${AZURE_CONFIGS}/$1;
  if [ ! -d "${chosen_dir}" ]; then
    echo "no config by that name"
    return 1;
  fi
  export AZURE_CONFIG_DIR=${chosen_dir};
}

function _azure_cli_config_switch_completion() {
  COMPREPLY=($(compgen -W "$(ls $AZURE_CONFIGS)" "${COMP_WORDS[1]}"))
}

complete -F _azure_cli_config_switch_completion caz

