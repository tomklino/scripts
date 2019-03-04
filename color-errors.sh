unalias echo 2>/dev/null

function _echo() {
  msg=$1;
  if [[ $msg =~ ^ERROR.+ ]]; then
    echo -e "\e[31m$msg\e[0m"
  else
    echo $msg
  fi
}

alias echo='_echo';
