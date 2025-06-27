#!/bin/sh

if [ $# -eq 0 ] ; then
    echo "Usage: $0 file.json"
    echo '\nReformats JSON to preferred format using `jq`.  Can specify multiple'
    echo 'files or use `*.json` to reformat all files in directory.'
    exit 1
fi

# default to SUCCESS
EXITCODE=0

for file in "$@"
do
	RESULT=$(jq --indent 2 --ascii-output . "$file")
	STATUS=$?
	if [ $STATUS -ne 0 ] ; then
		echo "^^^ errors parsing $file ^^^"

		# replace exit code with most recent failure
		EXITCODE=$STATUS
	else
		# use printf instead of echo to avoid possible backslash escaping
		printf "%s\n" "$RESULT" > "$file"
	fi
done

exit $EXITCODE
