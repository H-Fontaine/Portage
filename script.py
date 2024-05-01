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

        

load = gdb.Breakpoint("*0x80000c2")
#mod_exp = gdb.Breakpoint("*0x8001af4")
start_while = gdb.Breakpoint("*0x8001e90")
skip_leading_zero = gdb.Breakpoint("*0x8001fb2")
squaring = gdb.Breakpoint("*0x8001ede")
window = gdb.Breakpoint("*0x8001f32")
end = gdb.Breakpoint("*0x8001fb8")
#end_square = gdb.Breakpoint("*0x8001f0c")


class Breakpoints :
    LOAD = "*0x80000c2"
    MOD_EXP = "*0x8001af4"
    START_WHILE = "*0x8001e90"
    SKIP_LEADING_ZERO = "*0x8001fb2"
    SQUARING = "*0x8001ede"
    WINDOW = "*0x8001f32"
    END = "*0x8001fb8"



class Counter :
    COUNTER = 0
    
    def reset() :
        gdb.selected_inferior().write_memory(CYCCNT_register, int(0).to_bytes(4, 'little'))
        Counter.COUNTER = 0

    def read() :
        Counter.COUNTER = int.from_bytes(gdb.selected_inferior().read_memory(CYCCNT_register, 4).tobytes(), 'little')


class State :
    MOD_EXP_NB = 0
    END = False
    IN_WHILE = 0
    STATE = "null"
    DATA = [
        {"skip_leading_zero" : [],
         "squaring" : [],
         "window" :[]},

        {"skip_leading_zero" : [],
         "squaring" : [],
         "window" :[]},
        
        {"skip_leading_zero" : [],
         "squaring" : [],
         "window" :[]},

        {"skip_leading_zero" : [],
         "squaring" : [],
         "window" :[]}    
    ]


def breakpoint_handler(event) :
    match event.breakpoint.location:
        case Breakpoints.LOAD :
            P = nb.getPrime(PRIME_SIZE)
            Q = nb.getPrime(PRIME_SIZE)
            Key.set_key(P, Q, random.randint(0, P*Q-1))
            print(Key.N)
            Key.load_key()

        case Breakpoints.START_WHILE :
            if State.IN_WHILE == 1 :
                Counter.read()
                State.DATA[State.MOD_EXP_NB][State.STATE].append(Counter.COUNTER)
            else :
                State.IN_WHILE = 1
        
        case Breakpoints.SKIP_LEADING_ZERO :
            State.STATE = "skip_leading_zero"
            Counter.reset()

        case Breakpoints.SQUARING :
            State.STATE = "squaring"
            Counter.reset()
        
        case Breakpoints.WINDOW :
            State.STATE = "window"
            Counter.reset()

        case Breakpoints.END :
            Counter.read()
            State.DATA[State.MOD_EXP_NB][State.STATE].append(Counter.COUNTER)
            State.IN_WHILE = 0
            State.MOD_EXP_NB += 1
            State.STATE = "null"
            if State.MOD_EXP_NB == 4 :
                State.END = True
                print(State.DATA)
        
        case _:
            gdb.write("Not recognized breakpoint")

gdb.events.stop.connect(breakpoint_handler)

while not State.END :
    gdb.execute("continue")

print(State.DATA)