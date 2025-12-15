#!/bin/bash

# To ensure commits with modified maps always update _metadata.version,
# create a .git/hooks/pre-commit script that includes
# `exec tools/require-version-change.sh` as one of its lines.


CHANGED_MAPS=`git diff --name-only --staged | grep '\.map\.json' | wc -l`
NEW_VERSION=`git diff --staged | grep '^+    "version":' | wc -l`

if [[ "${CHANGED_MAPS}" != "${NEW_VERSION}" ]]; then
	echo "Only ${NEW_VERSION}/${CHANGED_MAPS} modified maps include _metadata.version update."
	git diff --staged | grep -E '^(\+    "version":)|(\+\+\+.*\.map\.json)'

	exit 1
fi

echo "Verified that all modified maps updated _metadata.version."
