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
    LOAD = "*0x80000c2"
    #MOD_EXP = "*0x8001af4"
    #START_WHILE = "*0x8001e90"
    #SKIP_LEADING_ZERO = "*0x8001fb2"
    
    # SQUARING_SELECT_BEGIN = "*0x8001ee6"
    # SQUARING_SELECT_END = "*0x8001eea"
    # SQUARING_MULT_BEGIN = "*0x8001f08"
    # SQUARING_MULT_END = "*0x8001f0c"
    
    WINDOW_S_SELECT_BEGIN = "*0x8001f40"
    WINDOW_S_SELECT_END = "*0x8001f44"
    # WINDOW_S_MULT_BEGIN = "*0x8001f62"
    # WINDOW_S_MULT_END = "*0x8001f66"
    
    # WINDOW_M_SELECT_BEGIN = "*0x8001f7c"
    # WINDOW_M_SELECT_END = "*0x8001f80"
    # WINDOW_M_MULT_BEGIN = "*0x8001f9e"
    # WINDOW_M_MULT_END = "*0x8001fa2"
    
    END = "*0x8001fb8"

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


class State :
    MOD_EXP_NB = 0
    END = False
    IN_WHILE = 0
    STATE = "null"
    DATA = [
        {"skip_leading_zero" : [],
         "squaring_select" : [],
         "squaring_mult" : [],
         "window_s_select" : [],
         "window_s_mult" : [],
         "window_m_select" : [],
         "window_m_mult" : []},
        
        {"skip_leading_zero" : [],
         "squaring_select" : [],
         "squaring_mult" : [],
         "window_s_select" : [],
         "window_s_mult" : [],
         "window_m_select" : [],
         "window_m_mult" : []},
        
        {"skip_leading_zero" : [],
         "squaring_select" : [],
         "squaring_mult" : [],
         "window_s_select" : [],
         "window_s_mult" : [],
         "window_m_select" : [],
         "window_m_mult" : []},
        
        {"skip_leading_zero" : [],
         "squaring_select" : [],
         "squaring_mult" : [],
         "window_s_select" : [],
         "window_s_mult" : [],
         "window_m_select" : [],
         "window_m_mult" : []}
    ]


def breakpoint_handler(event) :
    match event.breakpoint.location:
        case Breakpoints.LOAD :
            P = nb.getPrime(PRIME_SIZE)
            Q = nb.getPrime(PRIME_SIZE)
            Key.set_key(P, Q, random.randint(0, P*Q-1))
            print(Key.N)
            Key.load_key()

        # case Breakpoints.START_WHILE :
        #     if State.IN_WHILE == 1 :
        #         Counter.read()
        #         State.DATA[State.MOD_EXP_NB][State.STATE].append(Counter.COUNTER)
        #         print(State.DATA)
        #     else :
        #         State.IN_WHILE = 1
        
        # case Breakpoints.SKIP_LEADING_ZERO :
        #     State.STATE = "skip_leading_zero"
        #     Counter.reset()

        # case Breakpoints.SQUARING_SELECT_BEGIN :
        #     Counter.reset()
        
        # case Breakpoints.SQUARING_SELECT_END :
        #     Counter.read()
        #     State.DATA[State.MOD_EXP_NB]["squaring_select"].append(Counter.COUNTER)
        #     Counter.reset()

        # case Breakpoints.SQUARING_MULT_BEGIN :
        #     Counter.reset()

        # case Breakpoints.SQUARING_MULT_END :
        #     Counter.read()
        #     State.DATA[State.MOD_EXP_NB]["squaring_mult"].append(Counter.COUNTER)
        #     Counter.reset()

        case Breakpoints.WINDOW_S_SELECT_BEGIN :
            Counter.reset()
        
        case Breakpoints.WINDOW_S_SELECT_END :
            Counter.read()
            State.DATA[State.MOD_EXP_NB]["window_s_select"].append(Counter.COUNTER)
            Counter.reset()

        # case Breakpoints.WINDOW_S_MULT_BEGIN :
        #     Counter.reset()

        # case Breakpoints.WINDOW_S_MULT_END :
        #     Counter.read()
        #     State.DATA[State.MOD_EXP_NB]["window_s_mult"].append(Counter.COUNTER)
        #     Counter.reset()
        
        # case Breakpoints.WINDOW_M_SELECT_BEGIN :
        #     Counter.reset()
        
        # case Breakpoints.WINDOW_M_SELECT_END :
        #     Counter.read()
        #     State.DATA[State.MOD_EXP_NB]["window_m_select"].append(Counter.COUNTER)
        #     Counter.reset()
        
        # case Breakpoints.WINDOW_M_MULT_BEGIN :
        #     Counter.reset()
        
        # case Breakpoints.WINDOW_M_MULT_END :
        #     Counter.read()
        #     State.DATA[State.MOD_EXP_NB]["window_m_mult"].append(Counter.COUNTER)
        #     Counter.reset()

        case Breakpoints.END :
            Counter.read()
            State.IN_WHILE = 0
            State.MOD_EXP_NB += 1
            State.STATE = "null"
            if State.MOD_EXP_NB == 4 :
                State.END = True
        
        case _:
            gdb.write("Not recognized breakpoint")

gdb.events.stop.connect(breakpoint_handler)

while not State.END :
    gdb.execute("continue")

print(State.DATA)