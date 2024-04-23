import gdb
import Cryptodome.Util.number as nb

gdb.execute("b rsa.c:1089")
gdb.execute("b rsa.c:1090")

CYCCNT_register = 0xE0001004
gdb.selected_inferior().write_memory(CYCCNT_register, int(0).to_bytes(4, 'little'))
gdb.execute("c")
cycles_count = int.from_bytes(gdb.selected_inferior().read_memory(CYCCNT_register, 4).tobytes(), 'little')
print(cycles_count)


