#!/bin/bash

# USAGE: place all kube configuration files in the config defined in CONFIGS_DIR
#        then, use any of the commands:
#        use-kube-config <config-name> - to use the config by that name from the CONFIGS_DIR
#        use-pwd-kube-config to use a file named config in the current working directory
#        unset-kube-config to unset the kube config
CONFIGS_DIR=${HOME}/.kubeconfigs

function ckc() {
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

complete -F _kube_config_switch_completion ckc

# NOTE: Might not work if yq is installed using snap, due to snap confinment.
# Install from binaries provided by github instead.
function rename-context () {
	export new_name="$1"
	config_file=${KUBECONFIG:-"~/.kube/config"}
	yq e -i '.current-context as $current | .contexts[] |= (select(.name == $current) | .name = env(new_name)) | .current-context = env(new_name)' $config_file
	if ! [ -z $KUBECONFIG ]
	then
		mv $KUBECONFIG ${CONFIGS_DIR}/${new_name}
		export KUBECONFIG=${CONFIGS_DIR}/${new_name}
	fi
}

