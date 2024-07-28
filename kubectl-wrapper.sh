# Experimental kubectl pager wrapper
KUBECTL_CMD=$(whereis -b kubectl | awk '{print $2}')

function kubectl() {
  if awk '{for(i=1;i<=NF;i++) {if ($i == "-oyaml") exit 0}; exit 1}' <<< $@; then
    if [ -t 1 ] ; then
      $KUBECTL_CMD $@ | yq -C | less -KFX ;
    else
      $KUBECTL_CMD $@ | yq | less -KFX ;
    fi
  else
    $KUBECTL_CMD $@ | less -KFX
  fi
}

