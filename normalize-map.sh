#!/bin/sh

if [[ $# -eq 0 ]] ; then
    echo "Usage: $0 mapname.nv.json"
    echo '\nReformats JSON to preferred format using `jq`.  Can specify multiple'
    echo 'files or use `*.json` to reformat all files in directory.'
    exit 1
fi

for map in "$@"
do
    jq --indent 2 . "$map" > "$map.tmp" && mv "$map.tmp" "$map"
done
