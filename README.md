# CS516 - Project 2 - Modem output

### Description
Given simulated modem data recorded in a wav file (`message.wav`), determine the contents of the message.  This script expects the "answer" side of a 300 baud modem and that the data encodes ASCII text.


### Development
This is an ideal situation - no noise, there is no simultaneous outgoing transmission, and the frame window starts exactly at the beginning of the data.

The data is known to be the "answer" side of the communication so a bit is:
* one - "mark" - a 2225 Hz sine wave
* zero - "space" - a 2025 Hz sine wave

A byte is encoded as a space, 8 bits of data, then a mark.

So it is simply a matter of reading a bits worth of data, determining if it is zero or one, then validating and translating each collection of ten bits into an ASCII character.

### To run
Run with `uv` 

```commandline
uv run project2.py
```
