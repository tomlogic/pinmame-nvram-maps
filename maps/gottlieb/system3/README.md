Gottlieb System 3

Free Play on DMD games requires:
- coin door closed (switch 06)
- tournament switch flipped (switch 05)
- setting in memory (Cueball uses 0x0135; 1=on, 0=off)

It's possible to read switch status in memory.  On Cue Ball Wizard, addresses
0x0047, 0x0053, and 0x026C have bit 6 (0x40) set for door closed and 5 (0x20)
for tournament.
