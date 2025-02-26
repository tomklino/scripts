# jq common filters (when using kubectl <command> -o json)
alias jq-get-owner="jq '{ name: .metadata.name, owner: { kind: .metadata.ownerReferences[].kind, name: .metadata.ownerReferences[].name }}'"
alias jq-get-env="jq '.spec.template.spec.containers[].env'"
alias jq-get-volume-claim-templates="jq '.items[].spec.volumeClaimTemplates[]'"
alias jq-get-labels="jq '.metadata.labels'"
alias jq-get-selector="jq '.spec.selector'"
alias jq-get-rules="jq '.spec.rules'"

alias k-server-version="kubectl version -o yaml | yq r - 'serverVersion.gitVersion'"

alias kgp="kubectl get pod"
alias kgd="kubectl get deploy"
alias kgs="kubectl get sts"
alias kgi="kubectl get ing"

function kgetcrashloop() {
  crashlooppods=$(kubectl get pods -o json $@ | jq -r '.items[] | select(.status.containerStatuses[].state.waiting.reason == "CrashLoopBackOff") | .metadata.name')
  if [ ! -z $crashlooppods ]; then
    echo $crashlooppods| xargs kubectl get pods $@
  fi
}

function kexec() {
  kubectl exec -it $1 -- ${@:2}
}

function get-crd-short-names() {
  kubectl get crd -ojson |\
    jq -r --arg term "$1" \
      '.items[].spec.names |
       select(.singular | test($term)) |
       [.singular, ([.shortNames[]?]|join(","))] |
       @tsv' |\
    column -t
}

