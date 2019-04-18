#!/bin/bash


function sum_pods_memory_requests() {
  kubectl get pods $@ -o json |
    jq .items[].spec.containers[].resources.requests.memory |
    sed 's/\"//g' |
    grep -v null |
    numfmt --from=iec-i |
    awk '{s+=$1} END {printf "%.0f\n", s}' |
    numfmt --to iec-i
}

