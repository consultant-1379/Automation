#!/bin/bash

file_path=$1
epg_yaml_file=$2

if [ ! -f ${file_path} ]
then
    echo "File ${file_path} does not exist" >> /tmp/hash
    exit 1
fi


if [ ! -f ${file_path} ]
then
    echo "File ${epg_yaml_file} does not exist" >> /tmp/hash
    exit 1
fi

# get the line number of the epg.yaml entry
# the hash value is two lines below
line_no=$(grep -n epg.yaml ${file_path} | awk -F : '{ print $1 }')
hash_line=$((line_no + 2))
echo ${hash_line}

# get the hash value from the line found above
old_hash=$(sed "${hash_line}q;d" ${file_path} | awk '{ print $2 }')
echo "old hash ===>" ${old_hash} >> /tmp/hash

# get new hash
new_hash=$(sha256sum ${epg_yaml_file} | awk '{ print $1 }')
echo "new hash ===>" ${new_hash}  >> /tmp/hash
echo " " >> /tmp/hash


# update hash inline
sed -i "s/$old_hash/$new_hash/" ${file_path}
