#!/bin/bash

function get-region-of-mig () {
    project="$1"
    mig_name="$2"
    gcloud --project="$project" \
        compute instance-groups list \
        --filter="name = '$mig_name'" |\
        awk -v name="$mig_name" '$1 == name { print $2 }'
}

function get-all-instances () {
    project="$1"
    mig="$2"

    region=$(get-region-of-mig $project $mig)
    gcloud --project="$project" \
        compute instance-groups managed list-instances \
        --region="$region" \
        $mig \
        --format='table[no-heading](NAME)'
}

function recreate-all-instances() {
    project="$1"
    mig="$2"

    region=$(get-region-of-mig $project $mig)

    instances=$(get-all-instances $project $mig | xargs echo -n | sed 's/\ /,/g')

    gcloud --project="$project" \
        compute instance-groups managed recreate-instances \
        --region="$region" \
        --instances="$instances" \
        $mig
}

