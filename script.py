import gdb
import Cryptodome.Util.number as nb
import random

CYCCNT_register = 0xE0001004
NB_TESTS = 5
RSA_KEY_SIZE = 1024
RSA_KEY_SIZE_BYTES = RSA_KEY_SIZE // 8
PRIME_SIZE = RSA_KEY_SIZE // 2
PRIME_SIZE_BYTES = PRIME_SIZE // 8

gdb.execute("b main.c:65")
gdb.execute("b *0x8004a20")
gdb.execute("b *0x8004a28")

cycles_counts = []

for i in range(NB_TESTS):
    gdb.execute("c")

    if i != 0:
        ##BEGIN CONSISTENCY CHECK
        gdb_output = int.from_bytes(gdb.selected_inferior().read_memory(gdb.parse_and_eval("output").address, RSA_KEY_SIZE_BYTES).tobytes(), 'big')
        expected_output = pow(input, D, N)
        if gdb_output != expected_output:
            print("Test failed")
            break
        

    ##BEGIN LOADING VALUES
    E = 65537
    P = nb.getPrime(PRIME_SIZE)
    Q = nb.getPrime(PRIME_SIZE)
    N = P * Q
    PHI = (P-1)*(Q-1)
    D = pow(E, -1, PHI)
    input = random.randint(0, N-1)

    gdb.selected_inferior().write_memory(gdb.parse_and_eval("Q_buffer").address, Q.to_bytes(PRIME_SIZE_BYTES, 'big')) ##WRITING Q
    gdb.selected_inferior().write_memory(gdb.parse_and_eval("P_buffer").address, P.to_bytes(PRIME_SIZE_BYTES, 'big')) ##WRITING P
    gdb.selected_inferior().write_memory(gdb.parse_and_eval("N_buffer").address, N.to_bytes(RSA_KEY_SIZE_BYTES, 'big')) ##WRITING N
    gdb.selected_inferior().write_memory(gdb.parse_and_eval("D_buffer").address, D.to_bytes(RSA_KEY_SIZE_BYTES, 'big')) ##WRITING D
    gdb.selected_inferior().write_memory(gdb.parse_and_eval("input").address, input.to_bytes(RSA_KEY_SIZE_BYTES, 'big')) ##WRITING INPUT
    ##END LOADING VALUES

    gdb.execute("c")
    ##BEFORE ENCRYPTION
    gdb.selected_inferior().write_memory(CYCCNT_register, int(0).to_bytes(4, 'little'))
    gdb.execute("c")
    ##AFTER ENCRYPTION
    cycles_count = int.from_bytes(gdb.selected_inferior().read_memory(CYCCNT_register, 4).tobytes(), 'little')
    cycles_counts.append(cycles_count)

gdb.execute("shell clear")
print("Average cycles count: ", sum(cycles_counts) / len(cycles_counts))
print(cycles_counts)