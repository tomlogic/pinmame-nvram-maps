# Williams WPC RAM Mapping

## Introduction
In this document, I'll attempt to describe various regions of memory on
WPC games, including areas that aren't yet (or won't be) documented in
this project's maps.

Although the maps project uses integers in the JSON files, this README
uses hex throughout as you're likely to view an `.nv` file with a hex
editor as you follow along.

Some address boundaries will vary from game to game, as will the exact
location of certain variables.  Consulting the map for a given game can
aid in identifying exact locations.  For the majority of this document,
I'll use Demolition Man LX-4 (dm_lx4) for examples.

Williams WPC games have either 8KB or 12KB of memory.  Although all of
it is battery-backed, the game clears memory from 0x0000 to the byte before
the address used for Player 1's score (e.g., 0x172F on dm_lx4).  We can think
of this split as "working memory" (volatile, like RAM on a traditional
computer and not preserved when powered off) and "storage" (non-volatile,
like a hard disk).

## Non-Volatile Storage
Note that some areas use a 16-bit checksum to detect corrupted data.  See the
`checksum16` entry in map files for a list of checksummed regions and the
project's README for a description of how to calculate the sum.

### Game Scores
Let's start with the region that isn't erased at startup.  It begins with
game scores.  Either the current game in progress or the final scores from
the last game.  Because the game doesn't erase this region of memory on
startup, it can display the last game's scores, even after losing power in
the middle of a game.

On some games, scores consume 5 bytes.  On others, they use 6.  In all cases,
scores are in BCD (binary-coded decimal) format, so each nibble (half byte or
4 bits) represents a single digit of the score.  On games using 5 bytes, that
allows for scores up to 9.9B (ten 9's) and 6-byte games can go up to 999B
(twelve 9's).  The ROM itself might not display scores that large, but the
underlying WPC system code properly handles them.

In addition to the 24 bytes (4 * 6) of score data, there's an extra NUL
(0x00) byte between each score.  I found that all games had the sequence
`00 BC` after the scores -- its offset can help to identify whether  a game
uses 5-byte or 6-byte scores.

### Switch Counters
The next region holds 1-byte counters for detecting bad switches in a game.
It starts a few bytes after the `00 BC` marker.

At the start of each ball, the game decrements all counters by 1.  When
there's a switch hit, it resets the counter to its default value.  On a
Factory Reset, the game sets most bytes to 60.  Switches that are hit more
frequently will have a default of 10.  Others that are hit rarely might go
as high as 150 (seen on bop_l7).  Some switches are ignored by the switch
test and have a default of 0.

The size of this region varies from game to game.

### Poorly Documented Region
Following the switch counters is a region with limited documentation.
It includes a byte indicating the number of players for the current/last
game.  The ROM uses that field to know how many "last game" scores to
display during attract mode.

### Possible Mode Champions
Some games (e.g., cp_16, cv_14, and others) store one or more 16-bit
checksummed regions here with Mode Champions either instead of or in
addition to the mode champions toward the end of this memory.

### Possible Custom Message
On games with scores starting earlier (e.g., afm_113 starting at 0x16A0
versus dm_lx4 at 0x1730), there's room for two lines of "Custom Message"
in addition to custom messages stored later in memory.  The default for
this region is two sets of 32 spaces, a NUL, and 32 0xFF bytes, followed
by a 16-bit checksum.  This area always ends at 0x17FF

### Timestamp and Game ID
All WPC games (except the prototype Dr. Dude) have the same fields at
address 0x1800:
- 7-byte timestamp set to the current date and a time of 00:01 on boot.
  See the description of `wpc_rtc` in the project's README for details
  on what each byte represents.
- A 2-byte checksum of the timestamp.
- The WPC "system" software version as two bytes representing the "major"
  and "minor" version number.  On dm_lx4, those bytes are `03 15` and
  represent 3.21 (0x15 = 21).
- One byte representing the game's software version.  On early games like
  dm_lx4, it stores the LX-4 version as 0x04.  On later games like afm_113,
  it stores the 1.13 version as 0x11 (v1.1).
- This region ends with 5 bytes identifying the game.  On dm_lx4, it's
  `35 30 30 32 38` for the string "50028".

### Audits/Bookkeeping
All games store audits (referred to as Bookkeeping in the Service Menu)
in 6-byte blocks starting at 0x1811.  Games have different audit counts,
and the audit index for Standard Audits can vary as well.  See a game's
map file for identification of audit offsets.  If you're trying to
add audit's to a game's map, it can help to write different values to each
audit to see where they show up when viewed in the Service Menu.

Each audit starts with a 3-byte integer value indicating the lifetime audit
values, followed by a 2-byte integer for the current game's count of that
audit.  The last byte is an 8-bit checksum such that all 6 bytes add up to
0xFF.

Upon completion of a game, the ROM adds the 2-byte game audit to the 3-byte
lifetime audit and clears the game audit to 0.

Since each audit is checksummed separately, this section isn't protected by
a 16-bit checksum.

Note that some audits from the Service Menu are calculated on the fly using
multiple audits (e.g., Total Earnings, Freeplay Percent, Average Game Time).

Some games might have buggy code that attempts to correct invalid checksums.
During testing with `ft_l5`, we saw the audit byte sequence `00 00 0E 00
00 F2` alternate between a checksum of `F2` and `F0` on each boot, instead
of achieving the correct checksum of `F1`.

### Adjustments
Two-byte adjustments follow the audits, ending with a 16-bit checksum.  As
with the audits, the address of each adjustment doesn't necessarily match
the order on the Service Menu.

### Timestamps
The game stores multiple 7-byte timestamps after the adjustments.  Some of
them appear in "B.6 Timestamps".  Some games use this are for Mode Champion
dates (e.g., afm_113 stores the "Ruler of the Universe" timestamp here).

### High Scores
Four entries comprised of 3 bytes for the initials, and either 5 or 6 bytes
for a BCD-encoded score.  The ROM stores Buy-In High Scores in the section
allocated for Mode Champions.

### Grand Champion
A single entry with 3 bytes for the intiailze and either 5 or 6 bytes for
a BCD-encoded score.  The GC has its own checksum, and is kept intact after
resetting the high score table.

### High Score To Date (HSTD) Reset
Two 16-bit integers.  The first should match the games setting for number of
games between automatic HSTD reset.  The second is the current number of
games remaining before HSTD reset.

### Credits
Seven bytes encoding full credits in the first byte.  Remaining bytes aren't
fully documented.  Some notes:
- Second byte looks like **fractional** credits.  Unsure what the denominator
  is based on, but when testing with $0.75/credit the denominator seemed to be
  8 and rounded down (i.e. 3 for 1/3, 6 for 2/3).  Upon reaching that value,
  increments the credits and subtracts the denominator.
- Third byte seems to track **bonus* credits.  Upon reaching a certain level,
  it increments the credits and resets to 0.
- Fourth byte seemed to be an integer count of credit "units".  In the case
  of $0.75/credit this bye incremented by 3 on one coin drop and 12 on
  another (coin slots configured for $0.25 vs $1.00).

#### Example of dropping "quarters" when configured for "1/$0.75 4/$2.00"
| 0x1C98 | 0x1C99 | 0x1C9A | 0x1C9B | Credits | Notes                               |
|:------:|:------:|:------:|:------:|:-------:|-------------------------------------|
|   0    |   3    |   3    |   3    |   1/3   |                                     |
|   0    |   6    |   6    |   6    |   2/3   |                                     |
|   1    |   1    |   9    |   9    |    1    | Fractional credits rolls over at 8. |
|   1    |   4    |   12   |   12   |  1 1/3  |                                     |
|   1    |   7    |   15   |   15   |  1 2/3  |                                     |
|   2    |   2    |   18   |   18   |    2    | Fractional credits rolls over at 8. |
|   2    |   5    |   21   |   21   |  2 1/3  |                                     |
|   4    |   0    |   0    |   24   |    4    | Fractional rolls at 8, bonus at 24. |

### Volume
One byte ranging from 0 to 31 (0x1F) followed by a 16-bit checksum.  Note
that a Factory Reset sets an invalid volume/checksum of `FF FF FF`.  Changing
the volume or going into the service menu will reset it to a valid default.

### Undocumented Regions
Two regions with 16-bit checksums that haven't been documented yet.  On
dm_lx4, they're 10 bytes and 113 bytes long (including 2-byte checksum).

### Custom Messages
Two regions with space for a 3-line and 2-line Custom Message.

### Mode Champions
Multiple regions that may include Buy-In Scores, and separate regions for
different Mode Champion scores.


## Volatile Storage
The game uses memory below the player scores as working memory.  On startup,
the game performs a memory test of all memory locations from 0x0000 to the
address before player 1's score (so 0x172F on dm_lx4).  It starts by writing
0x55, then 0xAA, then 0x00, and finally a sequence of 16-bit values written
every 0x2F bytes (writing X + 0x2F to address X).  On dm_lx4, it starts by
writing 0x086F to 0x0840 and ends by writing 0x15A7 to 0x1578.

### Game State

#### "Fast Flips"
PinMAME identifies a "fast flips" byte (address 0x87 on dm_lx4) that
indicates whether the flippers are enabled (0x80) or not (0x00).

#### Attract/In Game
On dm_lx4, the byte at 0x8D has a value of 0 to indicate "in game" and 1
to indicate "attract mode".  Note that the game briefly switches to 0 and
back to 1 when entering and exiting the service menu.

#### Display Memory
On DMD-era WPC games, the service menu uses 0x160 for display memory.  Each
character uses 3 bytes.  The first is the character to display (0x00 for
none), if the second is 0x02, it displays a decimal point after the character,
and if the third is non-zero, it temporarily hides the text (used to flash
text -- 0x06 is a fast flash and 0x0A is a slow flash).

Line 1 starts at 0x160, line 2 at 0x190, line 3 at 0x1C0.  In testing, 0x1F0
looks like an alternate line 3.  It's probable that there are memory locations
that store the addresses of each line to display, and this is just scratch
memory.

#### Player/Ball
There's a series of 4 bytes with information on the game state.  On dm_lx4,
they are:
- 0x418: current_player (1 to 4)
- 0x419: current_ball (1 to n)
- 0x41A: extra_balls_left (0 to n)
- 0x41B: extra_balls_this_ball (0 to n).  This tracks the number of extra
  balls earned for a given ball.  Most games have an adjustment to set the
  maximum number of extra balls a player can earn on a single ball.

Bytes following this sequence also seem to be flags, but their meaning isn't
certain.

#### Current Time
On dm_lx4, two bytes representing the hour and minute as integers (as
opposed to BCD) at 0x43C and 0x43D.  Then a 7-byte WPC timestamp.

### Ball State
There's a region that stores state information for the current ball in play.
These are values that likely reset at the start of every ball, or at least
get seeded from the "player state" information later in memory.

Some examples from dm_lx4:
- 0x5E5-0x5E9: 5-byte BCD super jet value
- 0x5EA: remaining super jets
- 0x685-0x686: 2-byte BCD base value of ACMAG in 10-thousands (`06 00` = 6M)
- 0x687-0x68B: current 5-byte add-on to ACMAG (`00 07 37 50 00` = 6M + 7.375M)
- 0x68D-0x691: 5-byte BCD last collected ACMAG value
- 0x6A5-0x6A9: 5-byte BCD explode hurry-up value

### Player State
The game uses separate blocks of memory to store information specific to each
player.  On dm_lx4, that state information takes 69 bytes at starts at 0x72C
for player 1 (then 0x771, 0x7B6, 0x7FB for the other players).  Seeing 0x72C
stored at 0x4CE during a game.

Some decoded values for player 1 on dm_lx4:
- 0x74E-0x74F: 16-bit integer representing ball time in seconds
- 0x752: balls locked
- 0x755: lit/unawarded extra balls (stacked)
- 0x759: combos
- 0x75B: bonus multiplier
- 0x75D: side ramp hits
- 0x75F: claw: super jets started
- 0x760: claw: simon mode started
- 0x761: retina scans
- 0x765-0x769: retina value in 5 BCD bytes (resets to 5M on collect)
- 0x76A: last freeze standup award (in millions)
