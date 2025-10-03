Williams System 11 Notes
========================

Here are some notes on what's stored in memory.  All addresses are for 
High Speed (hs_l4) and could vary slightly for other games.

## Lamp Matrix
The game stores base lamp matrix values from 0x10 to 0x17 (column 1-8).  
There are other memory areas that override those values for light shows, but 
this memory encodes game state (e.g., bonus, bonus X) for the current ball.

## Display Memory
BCD-encoded values stored at 0x38 for ball/match display and 0x39 for credits.

## Game State
There's a series of bytes that reflect the state of the current game.  The
starting address varies by game, but this sequence appears to be consistent 
across games.

- 0xA8 "Tilted": Set to 0x68 when the player tilts.
- 0xA9 "Game Over": set to 0 during a game, 1 when the game is over.
- 0xAA: Set to 0xFF during end-of-ball and bonus routine, then 0x00 at the 
        start of the next ball.
- 0xAB: Unknown.
- 0xAC "Player Count": 0x00 = 1 player and 0x03 = 4 players.
- 0xAD "Current Player": 0x00 = 1 player and 0x03 = 4 players.
- 0xAE/0xAF: Big-endian address of current player's score (0x200, 0x204, 
             0x208, 0x20C).
- 0xB0: Extra balls.
- 0xB1/0xB2: Unknown, but frequently changes.
- 0xB3: Number of tilt warnings.

## Saved Player State
The game stores 26 bytes of saved state for each player at addresses 0x328,
0x342, 0x35C, and 0x376.  The saved state includes data from 0x10 to 0x1B 
(lamp matrix and other values), 0x30 to 0x37, and 0x02 to 0x07.
