import gdb
import Cryptodome.Util.number as nb
import random

CYCCNT_register = 0xE0001004
RSA_KEY_SIZE = 1024
RSA_KEY_SIZE_BYTES = RSA_KEY_SIZE // 8
PRIME_SIZE = RSA_KEY_SIZE // 2
PRIME_SIZE_BYTES = PRIME_SIZE // 8


class Loader :
    N = 0
    P = 0
    Q = 0
    R_inv = 0
    M1_mong = 0
    M2_mong = 0
    M3_mong = 0

    def generate_input() :
        Loader.P = nb.getPrime(PRIME_SIZE)
        Loader.Q = nb.getPrime(PRIME_SIZE)
        Loader.N = Loader.P * Loader.Q
        Loader.R_inv = pow(2**32, -1, Loader.N)
        Loader.M1_mong = random.randint(0, Loader.N-1) * 2**32 % Loader.N
        Loader.M2_mong = Loader.M1_mong**2 * Loader.R_inv % Loader.N
        Loader.M3_mong = Loader.M2_mong * Loader.M1_mong * Loader.R_inv % Loader.N
        return (Loader.P, Loader.Q, Loader.N, Loader.R_inv, Loader.M1_mong, Loader.M2_mong, Loader.M3_mong)

    def load() :
        gdb.selected_inferior().write_memory(gdb.parse_and_eval("m1_buffer").address, Loader.M1_mong.to_bytes(PRIME_SIZE_BYTES, 'big')) ##WRITING M1
        gdb.selected_inferior().write_memory(gdb.parse_and_eval("m2_buffer").address, Loader.M2_mong.to_bytes(PRIME_SIZE_BYTES, 'big')) ##WRITING M2
        gdb.selected_inferior().write_memory(gdb.parse_and_eval("m3_buffer").address, Loader.M3_mong.to_bytes(PRIME_SIZE_BYTES, 'big')) ##WRITING M3
        

class Breakpoints :
    LOAD = "*0x80000c2"

    def set_breakpoints() :
        for bp in Breakpoints.__dict__:
            if str(Breakpoints.__dict__[bp])[0] == '*':
                gdb.Breakpoint(str(Breakpoints.__dict__[bp]))


class Counter :
    COUNTER = 0
    
    def reset() :
        gdb.selected_inferior().write_memory(CYCCNT_register, int(0).to_bytes(4, 'little'))
        Counter.COUNTER = 0

    def read() :
        Counter.COUNTER = int.from_bytes(gdb.selected_inferior().read_memory(CYCCNT_register, 4).tobytes(), 'little')
        return Counter.COUNTER


def breakpoint_handler(event) :
    match event.breakpoint.location:
        case Breakpoints.LOAD :
            P, Q, N, R_inv, M1_mong, M2_mong, M3_mong = Loader.generate_input()
            Loader.load()
        
        case _:
            gdb.write("Not recognized breakpoint")


Breakpoints.set_breakpoints()
gdb.events.stop.connect(breakpoint_handler)
gdb.execute("continue")