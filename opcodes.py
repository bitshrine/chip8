import operator, random
from helpers.bit_operations import check_bit, format_hex

SUPPORT_C48 = True

def op(cpu, args):
    """
    Dummy function with the op function signature.
    `op` functions are of type (cpu, args) -> None
    """
    pass

def clear(cpu, args):
    cpu.display.clear()

def ret(cpu, args):
    cpu.pc = cpu.stack.pop()

def jump(cpu, args):
    cpu.pc = args['NNN']

def call(cpu, args):
    cpu.stack.push(cpu.pc)
    cpu.pc = args['NNN']

def skip_imm(predicate):
    def f(cpu, args):
        if (predicate(cpu.regs[args['X']], args['NN'])):
            cpu.pc += 2
    return f

def skip_reg(predicate):
    def f(cpu, args):
        if (predicate(cpu.regs[args['X']], cpu.regs[args['Y']])):
            cpu.pc += 2
    return f


def set_imm(cpu, args):
    cpu.regs[args['X']] = args['NN']

def add_imm(cpu, args):
    cpu.regs[args['X']] += args['NN']
    cpu.regs[args['X']] &= 0xFF

def set_reg(cpu, args):
    cpu.regs[args['X']] = cpu.regs[args['Y']]

def log_op(op):
    def f(cpu, args):
        cpu.regs[args['X']] = op(cpu.regs[args['X']], cpu.regs[args['Y']])
    return f


def add_reg(cpu, args):
    res = cpu.regs[args['X']] + cpu.regs[args['Y']]
    cpu.regs[0xF] = check_bit(res, 8)
    cpu.regs[args['X']] = res & 0xFF

def sub(first, second):
    def f(cpu, args):
        cpu.regs[0xF] = 1 if (cpu.regs[args[first]] > cpu.regs[args[second]]) else 0
        res = cpu.regs[args[first]] - cpu.regs[args[second]]
        cpu.regs[args['X']] = res & 0xFF
    return f


def shift(op, carry_pos):
    def f(cpu, args):
        if (not SUPPORT_C48):
            cpu.regs[args['X']] = cpu.regs[args['Y']]

        carry = check_bit(cpu.regs[args['X']], carry_pos)
        cpu.regs[0xF] = carry
        cpu.regs[args['X']] = op(cpu.regs[args['X']], 1) & 0xFF
    return f


def set_ir_imm(cpu, args):
    cpu.ir = args['NNN']

def jump_offset(cpu, args):
    if (not SUPPORT_C48):
        cpu.pc = (args['NNN'] + cpu.regs[args['X']]) & 0xFFF
    else:
        cpu.pc = (args['NNN'] + cpu.regs[0x0]) & 0xFFF

def gen_random(cpu, args):
    r = random.getrandbits(8)
    cpu.regs[args['X']] = r & args['NN']

def draw(cpu, args):
    X_start = cpu.regs[args['X']] % cpu.display.width
    Y = cpu.regs[args['Y']] % cpu.display.height
    N = args['N']

    cpu.regs[0xF] = 0

    # There has to be a nicer way to handle these
    # loops than interrupting them
    
    for i in range(N):
        X = X_start
        byte = cpu.memory[cpu.ir + i]
        for i_pixel in range(8):
            pixel = cpu.display.get(X, Y) == 1
            if (check_bit(byte, 7 - i_pixel) == pixel):
                cpu.display.set(X, Y, 0)
                cpu.regs[0xF] = 1
            elif (not pixel) and check_bit(byte, 7 - i_pixel):
                cpu.display.set(X, Y, 1)

            if (X == cpu.display.width - 1):
                break
            X += 1

        if (Y == cpu.display.height - 1):
            break
        Y += 1

def skip_key(predicate):
    def f(cpu, args):
        if(predicate(cpu.ihandler.get(cpu.regs[args['X']]))):
            cpu.pc += 2
            
    return f

def get_delay(cpu, args):
    cpu.regs[args['X']] = cpu.timer.read() & 0xFF

def set_delay(cpu, args):
    cpu.timer.set(cpu.regs[args['X']])

def set_sound(cpu, args):
    cpu.sound_timer.set(cpu.regs[args['X']])

def addri(cpu, args):
    res = cpu.ir + cpu.regs[args['X']]
    if (res & 0xFFF != 0):
        cpu.regs[0xF] = 1
    cpu.ir = res & 0xFFF

def wait_for_key(cpu, args):
    key = cpu.ihandler.get_any()
    if (key == -1):
        cpu.pc -= 2
    else:
        cpu.regs[args['X']] = key

def get_font(cpu, args):
    cpu.ir = cpu.FONTS_START + (cpu.regs[args['X']] * cpu.FONT_SIZE)

def dec_conversion(cpu, args):
    n = cpu.regs[args['X']]
    units = n % 10
    tens = int(((n - units) % 100) / 10)
    hundreds = int((n - tens) / 100)
    cpu.memory[cpu.ir:cpu.ir + 3] = [hundreds, tens, units]
    
def store(cpu, args):
    registers = range(args['X'] + 1)
    for r in registers:
        cpu.memory[cpu.ir + r] = cpu.regs[r]
    if (not SUPPORT_C48):
        cpu.ir += args['X'] + 1

def load(cpu, args):
    registers = range(args['X'] + 1)
    for r in registers:
        cpu.regs[r] = cpu.memory[cpu.ir + r]

def skip_if_pressed(cpu, args):
    if (cpu.ihandler.get(args['X'])):
        print(f"Key {args['X']} is pressed!")
        cpu.pc += 2
    

OPCODES = {
    '0x00E0': clear,
    '0x00EE': ret,
    '0x1NNN': jump,
    '0x2NNN': call,
    '0x3XNN': skip_imm(lambda a, b: a == b),#skip_eq_imm,
    '0x4XNN': skip_imm(lambda a, b: a != b),#skip_neq_imm,
    '0x5XY0': skip_reg(lambda a, b: a == b),#skip_eq_reg,
    '0x9XY0': skip_reg(lambda a, b: a != b),#skip_neq_reg,
    '0x6XNN': set_imm,
    '0x7XNN': add_imm,

    '0x8XY0': set_reg,
    '0x8XY1': log_op(operator.__or__),#or_reg,
    '0x8XY2': log_op(operator.__and__),#and_reg,
    '0x8XY3': log_op(operator.__xor__),#xor_reg,
    '0x8XY4': add_reg,
    '0x8XY5': sub('X', 'Y'), #sub_xy,
    '0x8XY7': sub('Y', 'X'), #sub_yx,

    '0x8XY6': shift(operator.__rshift__, 0),
    '0x8XYE': shift(operator.__lshift__, 7),

    '0xANNN': set_ir_imm,
    '0xBNNN': jump_offset,
    '0xCNNN': gen_random,

    '0xDXYN': draw,

    '0xEX9E': skip_key(lambda a: a),
    '0xEXA1': skip_key(lambda a: not a),

    '0xFX07': get_delay,
    '0xFX15': set_delay,
    '0xFX18': set_sound,

    '0xFX1E': addri,

    '0xFX0A': wait_for_key,

    '0xFX29': get_font,

    '0xFX33': dec_conversion,

    '0xFX55': store,
    '0xFX65': load
}

def get_code(main_id, args):
    code = None
    if (main_id == 0):
        code = '0x00E' + str(hex(args['N'])[2:]).upper()
    elif (main_id == 1):
        code = '0x1NNN'
    elif (main_id == 2):
        code = '0x2NNN'
    elif (main_id == 3):
        code = '0x3XNN'
    elif (main_id == 4):
        code = '0x4XNN'
    elif (main_id == 5):
        code = '0x5XY0'
    elif (main_id == 6):
        code = '0x6XNN'
    elif (main_id == 7):
        code = '0x7XNN'
    elif (main_id == 8):
        code = '0x8XY' + str(hex(args['N'])[2:]).upper()
    elif (main_id == 9):
        code = '0x9XY0'
    elif (main_id == 0xA):
        code = '0xANNN'
    elif (main_id == 0xB):
        code = '0xBNNN'
    elif (main_id == 0xC):
        code = '0xCNNN'
    elif (main_id == 0xD):
        code = '0xDXYN'
    elif (main_id == 0xE):
        code = '0xEX' + format_hex(args['NN'])
    elif (main_id == 0xF):
        code = '0xFX' + format_hex(args['NN'])
    return code
