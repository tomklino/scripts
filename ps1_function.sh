export PS1_ADDITIONS=();

function is_array() {
  if [[ "$(declare -p $1 2>/dev/null)" =~ "declare -a" ]]; then
    return 0;
  else
    return 1;
  fi
}

function ps1_additions() {
  if is_array "PS1_ADDITIONS"; then
    for addition in "${PS1_ADDITIONS[@]}"; do
      echo -n "${addition}"
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

