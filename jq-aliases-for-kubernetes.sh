alias jq-get-owner="jq '.items[] | { name: .metadata.name, owner: { kind: .metadata.ownerReferences[].kind, name: .metadata.ownerReferences[].name }}'"
alias jq-get-env="jq '.spec.template.spec.containers[].env'"
alias jq-get-volume-claim-templates="jq '.items[].spec.volumeClaimTemplates[]'"
alias jq-get-labels="jq '.metadata.labels'"
alias jq-get-selector="jq '.spec.selector'"
alias jq-get-rules="jq '.spec.rules'"

