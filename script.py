import gdb
import time
import Cryptodome.Util.number as nb
import struct

gdb.execute("b main.c:30")
gdb.execute("b main.c:55")
gdb.execute("b main.c:76")

gdb.Breakpoint("exit")

gdb.execute("continue")

P = nb.getPrime(1024)
Q = nb.getPrime(1024)
N = P * Q
E = 65537
phi = (P - 1) * (Q - 1)
D = pow(E, -1, phi)

gdb.execute("set var P_as_string=\"" + str(P) + "\"")
gdb.execute("set var Q_as_string=\"" + str(Q) + "\"")
gdb.execute("set var N_as_string=\"" + str(N) + "\"")
gdb.execute("set var D_as_string=\"" + str(D) + "\"")

print("Starting cyphering and decyphering")

gdb.execute("continue")

print("Passed consistancy check")

gdb.execute("continue")

modlen = int(gdb.parse_and_eval('modlen'))
print(modlen)

print(gdb.parse_and_eval("plain_text"))
print(gdb.selected_inferior().read_memory(gdb.parse_and_eval('plain_text').address, modlen))
plain_text = int.from_bytes(gdb.selected_inferior().read_memory(gdb.parse_and_eval('plain_text').address, modlen).tobytes(), 'big')
cipher_text = int.from_bytes(gdb.selected_inferior().read_memory(gdb.parse_and_eval('cipher_text').address, modlen).tobytes(), 'big')

print(plain_text)
print(cipher_text)

print(cipher_text == pow(plain_text, E, N))
print(plain_text == pow(cipher_text, D, N))