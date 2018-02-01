#!/bin/bash

base_url="https://unlimited.net.il";
index_page="/page/deployment_telaviv";
persistent_sum_file="${HOME}/.unlimited.sums"
tmp_sum_file="/tmp/unlimited.sums"

rm ${tmp_sum_file} > /dev/null
curl ${base_url}${index_page}\
       	| grep -Eo "src=\"/contentfiles[^\.]+\.png\"" | sed -r "s/src=\"(\/contentfiles[^\.]+\.png)\"/\1/"\
       	| while read img; do 
           curl ${base_url}${img} | sha1sum >> ${tmp_sum_file};
        done

if [ -f ${persistent_sum_file} ]; then
	diff -q ${persistent_sum_file} ${tmp_sum_file}
fi

cp ${tmp_sum_file} ${persistent_sum_file}
