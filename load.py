import gdb
import Cryptodome.Util.number as nb
import random

RSA_KEY_SIZE = 1024
RSA_KEY_SIZE_BYTES = RSA_KEY_SIZE // 8
PRIME_SIZE = RSA_KEY_SIZE // 2


N = 0
P = 0
Q = 0
R_inv = 0
M1_mong = 0
M2_mong = 0
M3_mong = 0
IDX = 0

P = nb.getPrime(PRIME_SIZE)
Q = nb.getPrime(PRIME_SIZE)
N = P * Q
R_inv = pow(2**32, -1, N)
M1_mong = random.randint(0, N-1) * 2**32 % N
M2_mong = M1_mong**2 * R_inv % N
M3_mong = M2_mong * M1_mong * R_inv % N
IDX = random.randint(2,3)
print(IDX)

gdb.selected_inferior().write_memory(gdb.parse_and_eval("m1_buffer").address, M1_mong.to_bytes(RSA_KEY_SIZE_BYTES, 'big')) ##WRITING M1
gdb.selected_inferior().write_memory(gdb.parse_and_eval("m2_buffer").address, M2_mong.to_bytes(RSA_KEY_SIZE_BYTES, 'big')) ##WRITING M2
gdb.selected_inferior().write_memory(gdb.parse_and_eval("m3_buffer").address, M3_mong.to_bytes(RSA_KEY_SIZE_BYTES, 'big')) ##WRITING M3
gdb.execute("set idx="+str(IDX))
        