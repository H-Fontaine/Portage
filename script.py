import gdb
import Cryptodome.Util.number as nb
import random

CYCCNT_register = 0xE0001004


gdb.execute("b main.c:47")
gdb.execute("b main.c:51")

gdb.execute("c")

#STOP BEGIN FOR LOOP
cycles_count = int.from_bytes(gdb.selected_inferior().read_memory(CYCCNT_register, 4).tobytes(), 'little')
print(cycles_count)
gdb.selected_inferior().write_memory(CYCCNT_register, int(0).to_bytes(4, 'big'))

gdb.execute("c")

#STOP END FOR LOOP
cycles_count = int.from_bytes(gdb.selected_inferior().read_memory(CYCCNT_register, 4).tobytes(), 'little')
print(cycles_count)