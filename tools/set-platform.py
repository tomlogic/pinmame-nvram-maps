#!/usr/bin/env python3
"""
Set the `platform` metadata for one or more `.nv.json` files.

- Add `_metadata.platform` attribute.
- Remove `endian`, `nibble`, and `ramsize` from `_metadata`.
- Increase all non-dipsw `start`, `end` and `offsets` properties by the
  base address of the platform's nvram entry.
"""

import argparse
import json
import os

from collections import OrderedDict
from typing import Union


def to_int(v: Union[int, str]) -> int:
    """Returns 'v' if already an int, otherwise assume a string and convert
    with a base of '0' (which handles leading 0 as octal and 0x as hex).
    (Code copied from py-pinmame-nvmaps project.)
    """
    if type(v) is int:
        return v
    return int(v, 0)

def shift_map_base(record: Union[list, dict], offset: int) -> None:
    """
    Recursively walk the map, looking for attributes to update.

    :param record: A portion of the map to process.
    :param offset: Base address of nvram area for this platform.
    :return: None
    """
    if type(record) is list:
        for item in record:
            shift_map_base(item, offset)
    elif type(record) in [dict, OrderedDict]:
        if record.get('encoding') == 'dipsw':
            # ignore DIP switch records
            return
        for key, value in record.items():
            if key in ['start', 'end', 'offsets']:
                record[key] = '0x%04X' % (to_int(value) + offset)
            else:
                shift_map_base(value, offset)


PLATFORM_DIR = os.path.join(os.path.dirname(__file__), '../platforms')

parser = argparse.ArgumentParser(description='Maps Platform Setter')
parser.add_argument('--platform', required=True,
                    help='platform (without .json extension) to apply')
parser.add_argument('maps', nargs='+')
args = parser.parse_args()

try:
    with open(os.path.join(PLATFORM_DIR, args.platform + '.json')) as platform_file:
        platform_json = json.load(platform_file)
except FileNotFoundError:
    print("Error couldn't open platforms/%s.json" % platform_file)
    exit(-1)

# find the first nvram entry in the platform file
area = None
for area in platform_json.get('memory_layout'):
    if area.get('type') == 'nvram':
        break
if not area:
    print("Error: unable to find nvram entry in platform's memory_layout.")
    exit(-1)

for file in args.maps:
    print('Adding platform to %s...' % file)
    errors = 0
    with open(file) as map_file:
        map_json = json.load(map_file, object_pairs_hook=OrderedDict)
    metadata = map_json.get('_metadata')
    existing_platform = metadata.get('platform')
    if existing_platform:
        print('...map already using platform %s' % existing_platform)
        continue
    map_endian = metadata.get('endian', '(undefined)')
    platform_endian = platform_json.get('endian', '(undefined)')
    if map_endian != platform_endian:
        print("Error: `endian` from map (%s) doesn't match value from platform (%s)"
              % (map_endian, platform_endian))
        errors += 1
    map_nibble = metadata.get('nibble', 'both')
    platform_nibble = area.get('nibble', 'both')
    if map_nibble != platform_nibble:
        print("Error: `nibble` from map (%s) doesn't match platform's nvram.nibble (%s)"
              % (map_nibble, platform_nibble))
        errors += 1

    # Some maps have the .nv file size for ramsize, but that includes
    # additional bytes appended by PinMAME.  Round down to a multiple of 128.
    map_ramsize = metadata.get('ramsize', 0) & 0xFFFFFF80
    platform_ramsize = to_int(area.get('size'))
    if map_ramsize and map_ramsize != platform_ramsize:
        print("Error: `ramsize` from map (%u) doesn't match platform's nvram.size (%u)"
              % (map_ramsize, platform_ramsize))
        errors += 1

    if errors:
        print("Aborting update of %s due to errors." % file)
        exit(-1)

    for attribute in ['endian', 'nibble', 'ramsize']:
        metadata.pop(attribute, None)

    # add platform to metadata, close to where endian/nibble/ramsize typically appeared
    metadata['platform'] = args.platform
    for entry in ['platform', 'license', 'copyright', 'version']:
        if entry in metadata:
            metadata.move_to_end(entry, last=False)

    nvram_base = to_int(area.get('address'))
    if nvram_base:
        print("Shifting map by 0x%X bytes..." % nvram_base)
        shift_map_base(map_json, nvram_base)

    with open(file, 'w') as outfile:
        outfile.write(json.dumps(map_json, indent=2))
        # add trailing newline to match `jq` output
        outfile.write('\n')
