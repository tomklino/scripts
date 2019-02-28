alias jq-get-owner="jq '.items[] | { name: .metadata.name, owner: { kind: .metadata.ownerReferences[].kind, name: .metadata.ownerReferences[].name }}'"
alias jq-get-env="jq '.spec.template.spec.containers[].env'"
alias jq-get-volume-claim-templates="jq -C '.items[].spec.volumeClaimTemplates[]'"

