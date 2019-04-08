#!/bin/bash

# USAGE: place all kube configuration files in the config defined in CONFIGS_DIR
#        then, use any of the commands:
#        use-kube-config <config-name> - to use the config by that name from the CONFIGS_DIR
#        use-pwd-kube-config to use a file named config in the current working directory
#        unset-kube-config to unset the kube config
CONFIGS_DIR=${HOME}/.kubeconfigs

function use-kube-config() {
  chosen_file=${CONFIGS_DIR}/$1;
  if [ ! -f "${chosen_file}" ]; then
    echo "no config by that name"
    return 1;
  fi
  export KUBECONFIG=${chosen_file};
}

function use-pwd-kube-config() {
  export KUBECONFIG=config;
}

function unset-kube-config() {
  export KUBECONFIG=/dev/null;
}

function _kube_config_switch_completion() {
  COMPREPLY=($(compgen -W "$(ls $CONFIGS_DIR)" "${COMP_WORDS[1]}"))
}

complete -F _kube_config_switch_completion use-kube-config

