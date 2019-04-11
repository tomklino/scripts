function ps1_additions() {
  if [ -d ${HOME}/.ps1_additions ]; then
    for addition in $(ls ${HOME}/.ps1_additions); do
      echo -n "$(${HOME}/.ps1_additions/${addition})"
    done
  else
    echo -n "";
  fi
}

function ps1_func() {
  local __user_and_host="\[\033[01;32m\]$(whoami)@$(hostname)";
  local __cur_location="\[\033[01;34m\]$(dirs)";

  local __prompt_tail="\[\033[35m\]$"
  local __writing_color="\[\033[00m\]"
  echo -ne "$__user_and_host $__cur_location $(ps1_additions)$__prompt_tail $__writing_color";
}

function set_bash_prompt() {
  export PS1=$(ps1_func)
}

export PROMPT_COMMAND='set_bash_prompt; echo -ne "\033]2;$(dirs +0)\007"'

