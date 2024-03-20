import gdb
import 


print("Hello, World!")

gdb.Breakpoint("main")
a = gdb.parse_and_eval("result")
print(str(a))
gdb.execute("set var result=\"abcdfeg\"")
a = gdb.parse_and_eval("result")
print(str(a))
