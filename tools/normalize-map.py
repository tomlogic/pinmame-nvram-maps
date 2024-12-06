#!/usr/bin/env python3

"""
Script to normalize the nvram map files:
  - One entry per line.
  - Indent with 2 spaces.

Usage:
    normalize-map.py mapname.nv.json
    normalize-map.py *.nv.json

File format updates
-------------------
* v0.3:
    - convert start/end values stored as hex strings to decimal values

* v0.2:
    - remove "packed"=true and replace "packed"=false with "nibble"="low"
"""

import json
import sys

# global to hold required file format for last converted file
file_format = 0.0

def minimum_file_format(v):
    global file_format

    if file_format < v:
        file_format = v


def map_convert(pairs):
    global file_format

    result = {}
    for k, v in pairs:
        if k == '_fileformat':
            file_format = v
        elif k == 'nibble':
            # "nibble" is only valid in v0.2 and later
            minimum_file_format(0.2)

        if k == 'packed':
            # as of v0.2, "packed" attribute deprecated in favor of "nibble"
            if not v:
                # replace packed=false with nibble=low
                result['nibble'] = 'low'
                minimum_file_format(0.2)
            # silently remove default packed=true
        elif k in ['start', 'end'] and isinstance(v, str) and v.startswith('0x'):
            # as of v0.3, deprecate start/end stored as hex
            # But file format is still valid as v0.1 or v0.2.
            result[k] = int(v, 16)
        elif k == 'offsets':
            offsets = []
            for offset in v:
                if isinstance(offset, str) and offset.startswith('0x'):
                    offsets.append(int(offset, 16))
                else:
                    offsets.append(offset)
            result[k] = offsets
        else:
            result[k] = v

    return result

exitcode = 0
for filename in sys.argv[1:]:
    file_format = 0.1       # default to 0.1 if _fileformat is missing from JSON
    try:
        data = json.load(open(filename, 'r'), object_pairs_hook=map_convert)
        data['_fileformat'] = file_format
        with open(filename, 'w') as outfile:
            outfile.write(json.dumps(data, indent=2))
            # add trailing newline to match `jq` output
            outfile.write('\n')
    except json.decoder.JSONDecodeError as e:
        print("JSON decode error(s) for %s:\n%s\n" % (filename, str(e)))
        # at least one JSON file was improperly formatted
        exitcode = 1

raise SystemExit(exitcode)
