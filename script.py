import gdb
import Cryptodome.Util.number as nb
import random

CYCCNT_register = 0xE0001004
NB_TESTS = 5
RSA_KEY_SIZE = 1024
RSA_KEY_SIZE_BYTES = RSA_KEY_SIZE // 8
PRIME_SIZE = RSA_KEY_SIZE // 2
PRIME_SIZE_BYTES = PRIME_SIZE // 8


class Key :
    N = 0
    P = 0
    Q = 0
    E = 65537
    PHI = (P-1)*(Q-1)
    D = pow(E, -1, PHI)
    INPUT = 0 

    def set_key(P, Q, INPUT) :
        Key.P = P
        Key.Q = Q
        Key.N = P * Q
        Key.PHI = (P-1)*(Q-1)
        Key.D = pow(Key.E, -1, Key.PHI)
        Key.INPUT = INPUT

    def load_key() :
        gdb.selected_inferior().write_memory(gdb.parse_and_eval("Q_buffer").address, Key.Q.to_bytes(PRIME_SIZE_BYTES, 'big')) ##WRITING Q
        gdb.selected_inferior().write_memory(gdb.parse_and_eval("P_buffer").address, Key.P.to_bytes(PRIME_SIZE_BYTES, 'big')) ##WRITING P
        gdb.selected_inferior().write_memory(gdb.parse_and_eval("N_buffer").address, Key.N.to_bytes(RSA_KEY_SIZE_BYTES, 'big')) ##WRITING N
        gdb.selected_inferior().write_memory(gdb.parse_and_eval("D_buffer").address, Key.D.to_bytes(RSA_KEY_SIZE_BYTES, 'big')) ##WRITING D
        gdb.selected_inferior().write_memory(gdb.parse_and_eval("input").address,  Key.INPUT.to_bytes(RSA_KEY_SIZE_BYTES, 'big')) ##WRITING INPUT




class Breakpoints :
    LOAD = "*0x80000b6"
    BEGIN_select = "*0x800161e"
    END_select = "*0x8001626"

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
            P = nb.getPrime(PRIME_SIZE)
            Q = nb.getPrime(PRIME_SIZE)
            Key.set_key(P, Q, random.randint(0, P*Q-1))
            print(Key.N)
            Key.load_key()

        case Breakpoints.BEGIN_select :
            Counter.reset()
        
        case Breakpoints.END_select :
            print("COUNTER :", Counter.read())
        
        case _:
            gdb.write("Not recognized breakpoint")

gdb.events.stop.connect(breakpoint_handler)
Breakpoints.set_breakpoints()

while True :
    gdb.execute("continue")