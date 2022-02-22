# Chip8 emulator

> Requirements: `numpy`, `pygame`, `tqdm` and `tk`

Python implementation of a Chip8 emulator, following several (Tobias V. Langhoff's [incredible writeup](https://tobiasvl.github.io/blog/write-a-chip-8-emulator/), and [Wikipedia](https://en.wikipedia.org/wiki/CHIP-8)) descriptions of the system. The goal of this particular project is to iterate on this emulator to eventually implement a full [XO-Chip](https://github.com/JohnEarnest/Octo) emulator.

This is not optimized at all!
- [x] Make it work
- [x] Make it right (ish)
- [ ] Make it fast

## Instructions
Download the whole project, and run [chip8.py](chip8.py) as follows:
```
python3 chip8.py [-d] [--rom=rom_path]
```

- The `-r` or `--rom` arguments can be used to provide a path to a ROM file. If no such path is provided, you will be promped with a file dialog.
- The `-d` or `--debug` arguments are not yet functional, but serve to start the emulator in debug mode, where the user can execute a single CPU cycle with the `tab` key, and print the state of the CPU with the `p` key.

The color scheme of the emulator can be changed by dragging and dropping theme files onto the running emulator. Examples of valid files can be found in the [themes](themes) folder.

The [Chip8 Archive](https://github.com/JohnEarnest/chip8Archive) is a great place to find ROMs to play with.




---
## TODO
- [ ] Allow command-line configuration of C48 support
- [ ] Add theme specification from command line
- [ ] Add pause button
- [ ] Add proper sound
- [ ] Implement debug mode
- [ ] Add reset functionality
- [ ] Add drag-n-drop ROM loading
- [ ] Add SuperChip instructions
- [ ] Add OctoChip instructions