import numpy as np

BYTE_MASK = 0xFF

def lo8(vec):
    """
    Get lower 8 bits of a bit vector.
    """
    return vec & BYTE_MASK

def hi8(vec):
    """
    Get high 8 bits of a bit vector
    """
    return (vec >> 8) & BYTE_MASK

def set(vec, i):
    """
    Set the i-th bit of the byte to 1
    """
    return vec | (1 << i)

def unset(vec, i):
    """
    Set the i-th bit of the vector to 0
    """
    return vec & ~(1 << i)

def check_bit(vec, i):
    """
    Returns the i-th bit of the vector
    """
    return 1 if ((vec & (1 << i)) != 0) else 0

def combine(sorted_asc, size=8):
    """
    Combine two or more bit vectors into a single one
    by appending them to one another. The `sorted_asc`
    parameter must be a `list()`-compatible collection
    of bit vectors such that the first one constitutes
    the lowest bits of the result. The `size` parameter
    determines the number of bits to shift per vector.

    ### Example
    ```
    >>> bits = (0xc, 0x0, 0xf)
    >>> combine(bits, size=4)
    (0xf0c)
    ```
    """
    sorted_asc = list(sorted_asc)
    res = 0
    while len(sorted_asc) > 0:
        res = (res << size) | sorted_asc.pop()
    return res

def nibble(vec, i=0):
    """Get the i-th nibble of the vector"""
    return (vec >> (i*4)) & 0xf

def format_hex(value):
    res = str(hex(value)[2:]).upper()
    if(len(res) == 1):
        res = '0' + res
    return res