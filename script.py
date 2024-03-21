import gdb
import Cryptodome.Util.number as nb

gdb.Breakpoint("main")



Q_as_string = gdb.parse_and_eval("Q_as_string")
P_as_string = gdb.parse_and_eval("P_as_string")

prime = nb.getPrime(1024)
print(prime)
gdb.execute("set var P_as_string=\"" + str(prime) + "\"")

prime = nb.getPrime(1024)
print(prime)
gdb.execute("set var Q_as_string=\"" + str(prime) + "\"")