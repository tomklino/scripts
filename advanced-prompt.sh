function color_my_prompt {
    local __ps1=""

    local __user_and_host="\[\033[01;32m\]\u@\h"
    local __cur_location="\[\033[01;34m\]\w"
    __ps1="$__ps1$__user_and_host $__cur_location "

    if (which git > /dev/null 2>&1); then
      local __git_branch_color="\[\033[31m\]"
      local __git_branch='`git branch 2> /dev/null | grep -e ^* | sed -E  s/^\\\\\*\ \(.+\)$/\(\\\\\1\)\ /`'
      __ps1="$__ps1$__git_branch_color$__git_branch"
    fi

    if (which kubectl > /dev/null 2>&1); then
      local __kube_prompt_color="\[\033[36m\]"
      local __kube_prompt='`kubectl config current-context 2>/dev/null | sed -E "s/^(.+)$/{\1} /"`'
      __ps1="$__ps1$__kube_prompt_color$__kube_prompt"
    fi

    if (which az > /dev/null 2>&1); then
      local __az_prompt_color="\[\033[37m\]"
      local __az_prompt='`echo ${AZURE_CONFIG_DIR:+${AZURE_CONFIG_DIR##*/}\ }`'
      __ps1="$__ps1$__az_prompt_color$__az_prompt"
    fi

    local __prompt_tail="\[\033[35m\]$"
    local __last_color="\[\033[00m\]"
    __ps1="$__ps1$__prompt_tail$__last_color "
    export PS1="$__ps1"
}

color_my_prompt
# set terminal title to current working directory
export PROMPT_COMMAND='echo -ne "\033]2;$(dirs +0)\007"'
