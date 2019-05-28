# jq common filters (when using kubectl <command> -o json)
alias jq-get-owner="jq '{ name: .metadata.name, owner: { kind: .metadata.ownerReferences[].kind, name: .metadata.ownerReferences[].name }}'"
alias jq-get-env="jq '.spec.template.spec.containers[].env'"
alias jq-get-volume-claim-templates="jq '.items[].spec.volumeClaimTemplates[]'"
alias jq-get-labels="jq '.metadata.labels'"
alias jq-get-selector="jq '.spec.selector'"
alias jq-get-rules="jq '.spec.rules'"

alias k-server-version="kubectl version -o yaml | yq r - 'serverVersion.gitVersion'"

