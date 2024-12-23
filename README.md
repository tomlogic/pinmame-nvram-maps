# PinMAME NVRAM Maps

The goal of this project is to document the contents of the `.nv` files
PinMAME uses to store the contents of a game's non-volatile RAM.  At a
basic level, it's useful to know how a game stores its high scores so
other programs (like a game launcher) can parse and display that
information.

Going further and documenting adjustments and audits allows for the
development of alternate interfaces (like a web browser) to view audits
and change game settings without using the service menu.

This project started in October 2015, and should be considered "beta"
quality.  As people map more games, the file format may change to
support additional requirements.

I chose to use [JSON](http://json.org) as a simple yet flexible file
format for this project.  If necessary, other projects should be able to
convert the map files to alternate formats.  The JSON website describes
the file format and includes links to parsing libraries in many
programming languages.

For this repository, we're formatting JSON files with each entry on its
own line, and 2 spaces for indentation.  You can get this formatting using
either `jq` or `python`:

- jq: `jq --indent 2 --ascii-output . mapname.nv.json`
- python: `json.dumps()` with the setting `indent=2`

```
    print(json.dumps(json.load(open('mapname.nv.json', 'r')), indent=2))
```

We're using the `--ascii-output` option to `jq` so it's consistent with the
Python output of bytes values 0x80 to 0xFF.  For example, `hs_l4.nv.json`
encodes a 0xC4 byte in the default attract text as `\u00C4`.

The script `tools/reformat-map.sh` can reformat one (or all) of the JSON
files using `jq`.  The script `tools/normalize-map.py` uses Python to do
the same formatting as `jq`, but also normalizes files to the latest format.

[Project home](https://github.com/tomlogic/pinmame-nvram-maps)

## License

This project is licensed under the GNU Lesser General Public License
v3.0 (LGPL).  LGPL requires that derived works be licensed under the
same license, but works that only link to it do not fall under this
restriction.

My intent is for the map files (`.nv.json`) to remain open and for
everyone to benefit from updates, yet allow for their use in
closed-source projects with attribution.  Please include a GitHub link
to the original project (or your fork of it), along with the
description, "This program makes use of content from the PinMAME NVRAM
Maps project."

## Sample Code

My preference is to keep this project dedicated to just the JSON files
so other projects can incorporate it as a git submodule.

A [related project](https://github.com/tomlogic/py-pinmame-nvmaps)
currently includes a Python program (`nvram_parser.py`) that works as a
standalone application to dump a parsed `.nv` file, or as a class
(ParseNVRAM) you can use from other programs.

There is also al [Rust library](https://github.com/francisdb/pinmame-nvram) 
for reading and writing nvram files that uses the maps from this project.

## Mapping New Games

Start PinMAME and write down all the high scores, and then exit. 
Open the game's `.nv` file in a hex editor and search for the initials. 
It should be possible to find each set of initials, with the
corresponding score nearby.

For adjustments, make a list of each setting, its default value, the
range of accepted values, and whether certain values have special
meaning (like *OFF* or *DISABLED*).  I make use of a modified version of
PinMAME that monitors an address range and dumps any changes it detects
to that range.  It's a simple matter to change a setting and see the
modified location in the NVRAM file.

Audits are a bit more difficult, and I intend to build a tool to modify
portions of the NVRAM file to aid in matching audits to file locations. 
Setting each 6-byte grouping to its starting address should allow for
quickly mapping each audit.

## File Format

The JSON file is essentially a big dictionary or associative array, with
the following key/value pairs.  It may help to review one or more of the
included files as an example of the file format while reading this
section of the documentation.

In cases where this specification isn't clear, please use existing maps
or the `nvram_parser.py` sample as a guide.

Numbers can appear as decimal values (`1234`) or hexadecimal values
inside of strings (`"0x4D2"`).  `_fileformat` v0.3 deprecated usage of
hexadecimal strings outside of the `mask` attribute.

### Meta Data

Note that keys starting with underscore describe the file itself, and
not the contents of the corresponding NVRAM file.

- **_roms** _(required)_: A list of PinMAME ROMs that use this map.
- **_fileformat** _(required)_: A `float` indicating the file format's
  version.  See Version History at the end of this file for changes.
- **_version** _(required)_: A `float` indicating the JSON file's version.
- **_copyright**: Original author of the file, possibly a list of people
  who have contributed to the file.
- **_license**: All files from this project are covered by the LGPL license.
  Modified map files, or maps created using an existing map as a starting
  point are also covered by that license.
- **_notes**: Notes about the file, possibly indicating who created it or
  portions of the file that may not be entirely correct.
- **_endian**: Set to either `"big"` or `"little"` to indicate the default
  byte order of multi-byte values.  Defaults to `"big"`.
  Refers to which end of the number is stored first.  For example, a
  `bcd`-encoded score of 123,450 is the byte sequence 0x12, 0x34, 0x50 if
  big-endian, and 0x50 0x34 0x12 if little-endian.
- **_nibble**: Set to `"both"` (default), `"high"`, or `"low"` to identify
  which 4-bit nibbles to use from each byte.  Some games (e.g., Williams
  System 7, Gottlieb System 80B, Stern M-100) used 4-bit NVRAM, so only
  half of each byte is valid.
  `"both"` indicates use of the full 8 bits/byte.  Set to `"low"` to use
  the lower 4 bits of the byte or `high` to use the upper 4 bits of the byte. 
  The `bcd` sequence `0x12 0x34 0x56` translates to `123456` when `nibble` is
  `both`, `246` when `nibble` is `low` and `135` when `nibble` is `high`.
  Robowars has an example of a `nibble=low` `ch` field, where the sequence
  `0x04 0x01 0x04 0x02 0x04 0x03` translates to `0x41 0x42 0x43` which is the
  string `"ABC"`.
  Stern Dracula and Wild Fyre (identical ROM) have examples of `nibble=high`.
- **_char_map**: Characters to use for the `ch` encoding instead of a straight 
  ASCII table.  See Whirlwind (`whirl_l3.nv.json`) as an example.

### Descriptors

The map file contains objects describing sections of the `.nv` file and
how to interpret them.  They're comprised of the following key/value pairs:

- **_note**: A note for someone maintaining the file; not displayed when
  processing an NVRAM file.

- **encoding** _(required)_ must be one of the following:
  - `"enum"`: An enumerated type where the byte at `start` is used as an
    index into a list of strings provided in `values`.
  - `"int"`: A (possibly) multibyte integer, where each byte is multiplied
    by a power of 256.  The byte sequence `0x12 0x34` would translate to the
    decimal value `4660`.
  - `"bits"`: Same decoding as `"int"`, but used to sum select integers from
    the list in `values`.
  - `"bcd"`: A binary-coded decimal value, where each byte represents two
    decimal digits of a number.  The byte sequence `0x12 0x34` would translate
    to the decimal value `1234`.  When converting BCD values, treat the
    nibbles 0xA to 0xF as 0 numerically, or a space for display purposes.
  - `"ch"`: A sequence of 7-bit ASCII characters that may be shortened by a
    null byte (0x00) terminator based on the `"null"` attribute for the entry.
    If the JSON file has a `_char_map` key, all bytes (including 0x00) are
	indexes into that string.
  - `"raw"`: A series of raw bytes, useful for extracting data yet to be
    decoded or that requires custom processing.
  - `"wpc_rtc"`: A special type for a real-time clock value
    from a WPC game, stored as a sequence of 7 bytes.  Starts with a
    two-byte year (2015 is `0x07 0xDF`), month (1-12), day of month (1-31),
    day of the week (0-6, 0=Sunday), hour (0-23) and minute (0-59).

- You must specify the location of data in the file using one or more of the
  following directives:
  - **start**: Offset into the `.nv` file of the first byte to
    interpret.  Default behavior is to use that single byte unless the `end`
    or `length` keys are present.  Either `start` or `offsets` are required.
  - **end**: Offset into the file of the last byte to interpret.  Its value
    must be greater than or equal to `start`. 
  - **length**: Number of bytes to interpret, must be at least 1 (default).
  - **offsets**: Alternative to using start/end or start/length when bytes
    aren't contiguous.  List of offsets to use.  Either `start` or `offsets`
    are required.

- These properties provide additional encoding details.
  - **endian**: Set to either `"big"` or `"little"` to indicate the byte
    order of multi-byte values.  Defaults to the `_endian` setting for the
    file (which defaults to `"big"`).
  - **nibble**: Defaults to file's `_nibble` setting (which defaults to
    `"both"`).  See `_nibble` for details.
  - **null**: Used for `"ch"` encodings to specify null (0x00) byte handling.
      For `truncate` and `terminate`, ignore all bytes after the null.
    - `"ignore"`: Ignore (skip over) null bytes.  Default setting.
    - `"truncate"`: A null can shorten the string, but won't be present for
      strings that fill the allotted space.
    - `"terminate"`: Null bytes are always present and terminate the string.
  - **packed**: Deprecated in favor of `nibble`.  Remove `packed=true` and
    replace `packed=false` with `nibble=low` (or set `_nibble` for the entire
    file).

- These properties are only related to displaying the value, independently of
  how it's actually stored in memory or a `.nv` file.
  - **label**: A label describing this collection of bytes in the `.nv` file. 
  - **short_label**: An optional, abbreviated label for use when space is
    limited (like in a game launcher on a DMD). 
  - **values**: A list of strings used for the `enum` encoding, starting at index 0.
    Also used for the `bits` encoding, as values for bit 0, 1, 2, etc.
  - **special_values**: A set of key/value pairs for a numeric field where some
    values have special meaning (for example, `{"0": "OFF"}`).
  - **units**: Used to indicate that a field contains a time value as either a
    number of `"seconds"` or `"minutes"`, and should be displayed as `HH:MM:SS`.
  - **suffix**: A string to append to the value (e.g., `"M"` if the value
    represents millions).
  - **scale**: A numeric multiplier for a decoded `int`, `bcd`, or `bits`.
  - **offset**: A numeric value to add to a decoded `int`, `bcd`, or `bits`
    value before displaying it.  Applied after `scale`.
  - **mask**: A mask to apply to each byte before processing.  For example, a
    mask of `"0x5F"` converts lowercase initials to uppercase and a mask of
    `"0x0F"` clears the upper four bits.

- Encodings can include properties that describe limitations imposed on
  adjustments in the service menu, or just ranges that the ROM considers
  invalid.  These all pertain to the stored value, exclusive of any `scale`
  or `offset`.
  - **default**: The factory default value.
    Used for the **initials** entry of a high score to indicate the value
    for an unused entry (e.g., `"   "` on WPC, `"\u0000\u0000\u0000"` on
    Gottlieb System 80).  Defaults to `0` unless specified.
  - **min** and **max**: The valid range of values.
  - **multiple_of**: Enforce a subset of values between `min` and `max`.
    Defaults to `1` (all values allowed) unless specified.

### File Map

Keys that don't start with an underscore typically have groups of
**descriptors** as their values.

- **last_played**: A descriptor (likely with a `wpc_rtc` encoding) with a
  date stamp of when PinMAME last saved the file.
- **last_game**: An array of up to four descriptors representing scores
  of the last game played on the machine.  A score of 0 indicates that the
  game had less than four players.
- **high_scores**: The traditional high score table that would usually
  start with the Grand Champion and then proceed through First Place to
  Fourth Place.  An array of objects with the following key/value pairs:
  - **label**: A label describing the score (e.g., `"Grand Champion"`).
  - **short_label**: An abbreviated label (e.g., `"GC"`).
  - **initials**: Descriptor of where the high score's initials are stored
    in the file.
  - **score**: Descriptor of where the high score's score is stored in the
    file.
- **mode_champions**: Another array of descriptors with recognition of
  other in-game accomplishments.
- **adjustments**: An object of key/value pairs for groupings of
  adjustments, where the key describes the group (e.g. `"A.1 Standard
  Adjustments"`) and the value is another object of key/value pairs
  for that grouping.  In that inner object, the keys are typically the
  numbers from the service menu (`"01"`) and the values are the
  corresponding descriptor.
- **audits**: Same as `adjustments`, but for the game's audits (also
  referred to as "Bookkeeping").
- **game_state**: A collection of memory areas used during a game to store
  the state of the game (e.g., player #, ball #, progressive jackpot value,
  etc.)  Not useful for PinMAME's `.nv` files, but could be referenced with
  custom code inside PinMAME.  See the High Speed map for an example.

### Checksums

The objects used for the last two entries in the file are
slightly different from the other descriptors.  They have the required
`start` field, require either an inclusive `end` (preferred) or `length`, and
`label` is optional.  They introduce an optional `groupings` key used to
treat a single descriptor as a list of groupings-sized ranges. 

(On WPC games, the audits are a series of 6-byte entries, each with an
8-bit checksum as the last byte.)

- **checksum8**: An array of memory regions protected by an 8-bit
  checksum.  The last byte of the range is set so that the low byte from
  the sum of all bytes in the range is `0xFF`.
- **checksum16**: An array of memory regions protected by a 16-bit
  checksum.  The last two bytes of the range are the 16-bit result of
  subtracting all prior bytes in the range from `0xFFFF`.

### Version History
- v0.1: Initial Version
- v0.2: Deprecate `packed` attribute in favor of `nibble`.
- v0.3: Deprecate usage of hex strings for `start`, `end` and `offsets`.
        Add the `null` attribute for entries with `ch` encoding.
- v0.4: Add global `_nibble` to apply to all entries.
