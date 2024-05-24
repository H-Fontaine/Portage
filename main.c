#include "mbedtls/rsa.h"
#include "mbedtls_dependencies.h"
#include "mbedtls/memory_buffer_alloc.h"
#include "acquisitions.h"

#define HEAP_SIZE_IN_BYTES 16000

#define SIZE_OF_RSA_KEY_IN_BITS 1024
#define SIZE_OF_P_AND_Q_IN_BITS (SIZE_OF_RSA_KEY_IN_BITS / 2)
#define SIZE_OF_RSA_KEY_IN_BYTES (SIZE_OF_RSA_KEY_IN_BITS / 8)
#define SIZE_OF_P_AND_Q_IN_BYTES (SIZE_OF_P_AND_Q_IN_BITS / 8)

#define NB_TESTS 5

unsigned char memory_buf[HEAP_SIZE_IN_BYTES];

int main() {
    mbedtls_memory_buffer_alloc_init(memory_buf, sizeof(memory_buf));

    user_defined_wrapper();
}
