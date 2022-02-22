NAME = "CHIP8 EMULATOR"
VERSION = 0.3

import sys, getopt

import pygame
import tkinter as tk
from tkinter import filedialog

from cpu import CPU
from rom_loader import rom_from_file

class Chip8:
    """
    Top-level class for the Chip8 emulator
    """
    def __init__(self, debug=False):
        pygame.init()
        self.cpu = CPU(debug)

    def run(self, rom):
        """
        Load a ROM into the Chip8 CPU and start
        execution. The ROM must be a list of bytes.
        """
        self.cpu.load_rom(rom)
        self.cpu.start()



if (__name__ == "__main__"):
    root = tk.Tk()
    root.withdraw()

    print(f"\n=========== {NAME} v{VERSION} ===========")

    opts = 'r:d'
    longopts = ['rom=', 'debug']

    path = None
    debug = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], opts, longopts)
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        sys.exit(2)

    for o, a in opts:
        if o in ("-r", "--rom"):
            path = a
        elif o in ("-d", "--debug"):
            debug = True
        else:
            assert False, "unhandled option"

    if (path == None):
        path = filedialog.askopenfilename()

    if (path == '' or path == None):
        print('No ROM file chosen. Exiting.\n')
        exit(0)

    chip8 = Chip8(debug)
    rom = rom_from_file(path)
    chip8.run(rom)


