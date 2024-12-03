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


def map_convert(pairs):
    result = {}
    for k, v in pairs:
        if k == 'packed':
            # as of v0.2, "packed" attribute deprecated in favor of "nibble"
            if not v:
                # replace packed=false with nibble=low
                result['nibble'] = 'low'
            # remove packed=true
        elif k in ['start', 'end'] and isinstance(v, str) and v.startswith('0x'):
            # as of v0.3, deprecate start/end stored as hex
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


for filename in sys.argv[1:]:
    data = json.load(open(filename, 'r'), object_pairs_hook=map_convert)

    data['_fileformat'] = 0.3
    with open(filename, 'w') as outfile:
        outfile.write(json.dumps(data, indent=2))
        outfile.write('\n')
