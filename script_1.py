import gdb
import Cryptodome.Util.number as nb
import random

gdb.execute("b main.c:68") ##BEGIN LOADING VALUES

NB_TESTS = 1000

RSA_KEY_SIZE = 1024
RSA_KEY_SIZE_BYTES = RSA_KEY_SIZE // 8
PRIME_SIZE = RSA_KEY_SIZE // 2
PRIME_SIZE_BYTES = PRIME_SIZE // 8


E = 65537

test = True



for i in range(NB_TESTS):
    gdb.execute("c") ##run

    if i != 0:
        ##BEGIN CONSISTENCY CHECK
        # import_ret = gdb.parse_and_eval("import_ret")
        # complete_ret = gdb.parse_and_eval("complete_ret")
        # privkeycheck_ret = gdb.parse_and_eval("key_check_ret")
        # public_ret = gdb.parse_and_eval("public_ret")
        # private_ret = gdb.parse_and_eval("private_ret")
        cipher_text_gdb = int.from_bytes(gdb.selected_inferior().read_memory(gdb.parse_and_eval("cipher_text").address, RSA_KEY_SIZE_BYTES).tobytes(), 'big')
        decrypted_text_gdb = int.from_bytes(gdb.selected_inferior().read_memory(gdb.parse_and_eval("decrypted_text").address, RSA_KEY_SIZE_BYTES).tobytes(), 'big')

        cipher_text_ret = cipher_text_gdb == cipher_text
        decrypted_text_ret = decrypted_text_gdb == plain_text

        """import_ret != 0 or complete_ret != 0 or privkeycheck_ret != 0 or public_ret != 0 or private_ret != 0 or"""
        if not(cipher_text_ret) or not(decrypted_text_ret) : 
            test = False
            log_file = open("log.txt", "w")
            # log_file.write("import_ret: " + str(import_ret) + "\n")
            # log_file.write("complete_ret: " + str(complete_ret) + "\n")
            # log_file.write("privkeycheck_ret: " + str(privkeycheck_ret) + "\n")
            # log_file.write("public_ret: " + str(public_ret) + "\n")
            # log_file.write("private_ret: " + str(private_ret) + "\n")
            log_file.write("cipher_text_ret: " + str(cipher_text_ret) + "\n")
            log_file.write("decrypted_text_ret: " + str(decrypted_text_ret) + "\n")
            log_file.write("P: " + str(P) + "\n")
            log_file.write("Q: " + str(Q) + "\n")
            log_file.write("N: " + str(N) + "\n")
            log_file.write("D: " + str(D) + "\n")
            log_file.close()
            break
        else : 
            print("OK : Test " + str(i) + " passed")
        
    ##BEGIN LOADING VALUES
    P = nb.getPrime(PRIME_SIZE)
    Q = nb.getPrime(PRIME_SIZE)
    N = P * Q
    PHI = (P-1)*(Q-1)
    D = pow(E, -1, PHI)
    plain_text = random.randint(0, N-1)
    cipher_text = pow(plain_text, E, N)

    gdb.selected_inferior().write_memory(gdb.parse_and_eval("Q_buffer").address, Q.to_bytes(PRIME_SIZE_BYTES, 'big')) ##WRITING Q
    gdb.selected_inferior().write_memory(gdb.parse_and_eval("P_buffer").address, P.to_bytes(PRIME_SIZE_BYTES, 'big')) ##WRITING P
    gdb.selected_inferior().write_memory(gdb.parse_and_eval("N_buffer").address, N.to_bytes(RSA_KEY_SIZE_BYTES, 'big')) ##WRITING N
    gdb.selected_inferior().write_memory(gdb.parse_and_eval("D_buffer").address, D.to_bytes(RSA_KEY_SIZE_BYTES, 'big')) ##WRITING D
    gdb.selected_inferior().write_memory(gdb.parse_and_eval("plain_text").address, plain_text.to_bytes(RSA_KEY_SIZE_BYTES, 'big')) ##WRITING PLAINTEXT
    ##END LOADING VALUES


print("Test result : " +str(test))