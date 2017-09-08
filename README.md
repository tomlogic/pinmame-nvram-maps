# PinMAME NVRAM Maps

The goal of this project is to document the contents of the `.nv` files
PinMAME uses to store the contents of a game's non-volatile RAM.  At a
basic level, it's useful to know how a game stores its high scores so
other programs (like a game launcher) can parse and display that
information.

Going further and documenting adjustments and audits allows for the
development of alternate interfaces (like a web browser) to view audits
and change game settings without using the service menu.

This project started in October 2015, and should be considered "alpha"
quality.  As people map more games, the file format may change to
support additional requirements.

I chose to use [JSON](http://json.org) as a simple yet flexible file
format for this project.  If necessary, other projects should be able to
convert the map files to alternate formats.  The JSON website describes
the file format and includes links to parsing libraries in many
programming languages.

[Project home](https://github.com/tomlogic/pinmame-nvram-maps)

## License

This project is licensed under the GNU Lesser General Public License
v3.0 (LGPL).  LGPL requires that derived works be licensed under the
same license, but works that only link to it do not fall under this
restriction.

My intent is for the map files (`.nv.json`) to remain open and for
everyone to benefit from updates, yet allow for their use in
closed-source projects with attribution.  Please include a Github link
to the original project (or your fork of it), along with the
description, "This program makes us of content from the PinMAME NVRAM
Maps project."

## Sample Code

My preference is to keep this project dedicated to just the JSON files
so other projects can incorporate it as a git submodule.

A [related project](https://github.com/tomlogic/py-pinmame-nvmap)
currently includes a Python program (`nvram_parser.py`) that works as a
standalone application to dump a parsed `.nv` file, or as a class
(ParseNVRAM) you can use from other programs.

## Mapping New Games

Start PinMAME and write down all of the high scores, and then exit. 
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
inside of strings (`"0x4D2"`).  Most map files will only use hex for
file offsets.

### Meta Data

Note that keys starting with underscore describe the file itself, and
not the contents of the corresponding NVRAM file.

- **_roms** _(required)_: A list of PinMAME ROMs that use this map.
- **_fileformat** _(required)_: Currently `0.1`.
- **_version** _(required)_: A `float` indicating the JSON file's version.
- **_copyright**: Original author of the file, possibly a list of people
  who have contributed to the file.
- **_license**: All files from this project are covered by the LGPL license.
  Modified map files, or maps created using an existing map as a starting
  point are also covered by that license.
- **_notes**: Notes about the file, possibly indicating who created it or
  portions of the file that may not be entirely correct.

### Descriptors

The map file contains objects describing sections of the `.nv` file and
how to interpret them.  They're comprised of the following key/value pairs:

- **label**: A label describing this collection of bytes in the `.nv` file. 
- **short_label**: An optional, abbreviated label for use when space is
  limited (like in a game launcher on a DMD). 
- **encoding** _(required)_:  One of the following:
  - `"enum"`: An enumerated type where the byte at `start` is used as an
    index into a list of strings provided in `values`.
  - `"int"`: A (possibly) multi-byte integer, where each byte is multiplied
    by a power of 256.  The byte sequence `0x12 0x34` would translate to the
    decimal value `4660`.
  - `"bcd"`: A binary-coded decimal value, where each byte represents two
    decimal digits of a number.  The byte sequence `0x12 0x34` would translate
    to the decimal value `1234`.
  - `"ch"`: A sequence of 7-bit ASCII characters.
  - `"wpc_rtc"`: A special type for a real-time clock value
    from a WPC game, stored as a sequence of 7 bytes.  Starts with a
    two-byte year (2015 is `0x07 0xDF`), month (1-12), day of month (1-31),
    day of the week (0-6, 0=Sunday), hour (0-23) and minute (0-59).
- **start** _(required)_: Offset into the `.nv` file of the first byte to
  interpret.  Default behavior is to use that single byte unless the `end`
  or `length` keys are present. 
- **end**: Offset into the file of the last byte to interpret.  Its value
  must be greater than or equal to `start`. 
- **length**: Number of bytes to interpret, must be at least 1 (default value). 
- **min** and **max**: Used for adjustments to specify its valid range of
  values.
- **default**: Used for adjustments to specify the factory default value.
  Used for the **initials** entry of a high score to indicate the value
  for an empty entry (e.g., `"   "` on WPC, `"\u0000\u0000u0000"` on
  Gottlieb System 80).  Defaults to `0` unless specified.
- **values**: A list of strings used for the `enum` encoding, starting at index 0.
- **special_values**: A set of key/value pairs for numeric field where some
  values have special meaning (for example, `{"0": "OFF"}`).
- **units**: Used to indicate that a field contains a time value as either a
  number of `"seconds"` or `"minutes"`, and should be displayed as `HH:MM:SS`.
- **suffix**: A string to append to the value (e.g., `"M"` if the value
  represents millions).
- **scale**: A numeric multiplier for a decoded `int` or `bcd`.
- **offset**: A numeric value to add to a decided `int` or `bcd` value
  before displaying it.  Applied after `scale`.
- **packed**: A boolean for `ch` and `bcd` types indicating use of 4 bits/byte
  (`false`) or 8 bits/byte (`true`).  Defaults to `true`.
- **_note**: A note for someone maintaining the file; not displayed when
  processing an NVRAM file.

### File Map

Keys that don't start with an underscore typically have groups of
**descriptors** as their values.

- **endian**: Set to either `"big"` or `"little"` to indicate the byte
  order of multi-byte values in the ROM file.  Defaults to `"big"`.
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

### Checksums

The objects used for the last two entries in the file are
slightly different from the other descriptors.  They have the required
`start` field, require either an `end` (preferred) or `length`, and
`label` is optional.  They introduce an optional `groupings` key used to
treat a single descriptor as a list of equally-sized groupings.

(On WPC games, the audits are a series of 6-byte entries, each with an
8-bit checksum as the last byte.)

- **checksum8**: An array of memory regions protected by an 8-bit
  checksum.  The last byte of the range is set so that the low byte from
  the sum of all bytes in the range is `0xFF`.
- **checksum16**: An array of memory regions protected by a 16-bit
  checksum.  That last two bytes of the range are set so that adding
  all other bytes in the range results in a value of `0xFFFF`.

