function aws-all-dns-records() {
  aws route53 list-hosted-zones | \
    jq '.HostedZones[].Id' | tr -d '"' | \
    while read zone; do
      aws route53 list-resource-record-sets --hosted-zone-id $zone | \
      jq '.ResourceRecordSets[] | select(.Type == "A" or .Type == "CNAME") | .Name' | \
      tr -d '"' | \
      sed 's|\\\\052|*|g'; # replacing asterisk escape code with asterisk
    done
}

