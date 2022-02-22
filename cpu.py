import numpy as np
import pygame
import json, os, sys

from helpers.bit_operations import combine, nibble
from rom_loader import rom_from_file

from stack import Stack
from display import Display
from timer import Timer, SoundTimer
from helpers.input_handler import InputHandler

from opcodes import OPCODES, get_code

MAX_FPS = 300

MEM_SIZE = 4096
NUM_REGISTERS = 16
ROM_START = 0x200
IR_START = 0x0

fonts = [
    0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
    0x20, 0x60, 0x20, 0x20, 0x70, # 1
    0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
    0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
    0x90, 0x90, 0xF0, 0x10, 0x10, # 4
    0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
    0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
    0xF0, 0x10, 0x20, 0x40, 0x40, # 7
    0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
    0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
    0xF0, 0x90, 0xF0, 0x90, 0x90, # A
    0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
    0xF0, 0x80, 0x80, 0x80, 0xF0, # C
    0xE0, 0x90, 0x90, 0x90, 0xE0, # D
    0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
    0xF0, 0x80, 0xF0, 0x80, 0x80 # F
]

class CPU:
    """
    Chip8 CPU, encapsulating all registers, the stack, the PC and IR registers,
    the RAM, both timers, and the display.
    """

    FONTS_START = 0x50
    FONTS_END = 0xA0
    FONT_SIZE = 5

    def __init__(self, debug=False):
        self.regs = np.array([0x0] * NUM_REGISTERS)
        self.stack = Stack()
        self.pc = ROM_START
        self.ir = IR_START

        self.memory = np.zeros(shape=(MEM_SIZE, ), dtype=np.uint8)
        self.memory[self.FONTS_START:self.FONTS_END] = fonts

        self.sound_timer = SoundTimer()
        self.timer = Timer()
        pygame.time.set_timer(pygame.USEREVENT+1, int(1000/60))

        self.display = Display()

        self.ihandler = InputHandler()

        self.DEBUG_MODE = debug

    def load_rom(self, rom):
        """
        Load a list of bytes into the CPU's memory.
        """
        self.memory[ROM_START:ROM_START + len(rom)] = rom

    def start(self):
        clock = pygame.time.Clock()

        while True:
            # self.handle_events()

            clock.tick(MAX_FPS)
            if (self.handle_events()):
                self.sound_timer.beep()
                self.iterate()
                self.display.draw()

    #def reload(self, rom_path):
    #    self.__init__(self.debug)
    #    rom = rom_from_file(rom_path)
    #    self.load_rom(rom)
    #    self.start()

    
    def fetch(self):
        """
        Fetch the next opcode from memory, and increment the PC
        """
        opcode = combine((self.memory[self.pc + 1], self.memory[self.pc]), size=8)
        self.pc += 2
        return opcode


    def decode(self, opcode):
        """
        Transform the opcode into a callable function and
        a dict of arguments.
        """
        args = {
            'X': nibble(opcode, 2),
            'Y': nibble(opcode, 1),
            'N': opcode & 0xf,
            'NN': opcode & 0xff,
            'NNN': opcode & 0xfff,
        }
        main_id = nibble(opcode, 3)
        code = get_code(main_id, args)
        return OPCODES[code], args
        

    def iterate(self):
        """
        Perform one iteration of fetch-decode-execute
        """
        opcode = self.fetch()
        op, args = self.decode(opcode)
        op(self, args)

    def handle_events(self):

        cont_execution = False

        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                sys.exit()

            elif (event.type == pygame.USEREVENT + 1):
                self.timer.countDown()

            elif (event.type == pygame.KEYDOWN):
                self.ihandler.set(event.key, True)

            elif (event.type == pygame.KEYUP):
                if (self.DEBUG_MODE):
                    if (event.key == pygame.K_TAB):
                        cont_execution = True
                    elif (event.key == pygame.K_p):
                        print(self)
                else:
                    self.ihandler.set(event.key, False)

            # Drag-n-drop theme support 
            elif (event.type == pygame.DROPFILE):
                extension = os.path.splitext(event.file)[1]
                if (extension == '.c8t'):
                    with open(event.file) as f:
                        new_colors_str = json.load(f)
                        for k, v in new_colors_str.items():
                            self.display.COLORS.update({int(k): v})

        if (not self.DEBUG_MODE):
            cont_execution = True

        return cont_execution

    def __str__(self):
        return f"\
        [CPU]\n\
        Registers:\t{list(map(hex, self.regs))}\n\
        PC:\t{hex(self.pc)}\n\
        IR:\t{hex(self.ir)}\n\
        Timer:\t{self.timer.read()}\n\
        "
            