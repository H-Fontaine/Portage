#include "mbedtls/rsa.h"
#include "mbedtls_dependencies.h"
#include "mbedtls/memory_buffer_alloc.h"

#define HEAP_SIZE_IN_BYTES 16000

#define SIZE_OF_RSA_KEY_IN_BITS 1024
#define SIZE_OF_P_AND_Q_IN_BITS (SIZE_OF_RSA_KEY_IN_BITS / 2)
#define SIZE_OF_RSA_KEY_IN_BYTES (SIZE_OF_RSA_KEY_IN_BITS / 8)
#define SIZE_OF_P_AND_Q_IN_BYTES (SIZE_OF_P_AND_Q_IN_BITS / 8)

#define NB_TESTS 1000

unsigned char memory_buf[HEAP_SIZE_IN_BYTES];

int main() {
    mbedtls_memory_buffer_alloc_init(memory_buf, sizeof(memory_buf));

    int ret = 0;
    
    mbedtls_mpi P, Q, N, D, E;
    mbedtls_mpi_init(&P);
    mbedtls_mpi_init(&Q);
    mbedtls_mpi_init(&N);
    mbedtls_mpi_init(&D);
    mbedtls_mpi_init(&E);
    mbedtls_rsa_context rsa;
    mbedtls_rsa_init(&rsa);

    const unsigned char Q_buffer[SIZE_OF_P_AND_Q_IN_BYTES]; 
    const unsigned char P_buffer[SIZE_OF_P_AND_Q_IN_BYTES]; 
    const unsigned char N_buffer[SIZE_OF_RSA_KEY_IN_BYTES]; 
    const unsigned char D_buffer[SIZE_OF_RSA_KEY_IN_BYTES];

    unsigned char plain_text[SIZE_OF_RSA_KEY_IN_BYTES];
    unsigned char cipher_text[SIZE_OF_RSA_KEY_IN_BYTES];
    unsigned char decrypted_text[SIZE_OF_RSA_KEY_IN_BYTES];
    
    mbedtls_mpi_lset(&E, 65537);

    int import_ret = 2;
    int complete_ret = 2;
    int key_check_ret = 2;
    int public_ret = 2;
    int private_ret = 2;

    
    for (size_t i = 0; i < NB_TESTS; i++)
    {
        mbedtls_rsa_free(&rsa);
        mbedtls_mpi_free(&P);
        mbedtls_mpi_free(&Q);
        mbedtls_mpi_free(&N);
        mbedtls_mpi_free(&D);

        mbedtls_rsa_init(&rsa);
        
        mbedtls_mpi_init(&P);
        mbedtls_mpi_init(&Q);
        mbedtls_mpi_init(&N);
        mbedtls_mpi_init(&D);

        memset((void*)Q_buffer, 0, sizeof(Q_buffer));
        memset((void*)P_buffer, 0, sizeof(P_buffer));
        memset((void*)N_buffer, 0, sizeof(N_buffer));
        memset((void*)D_buffer, 0, sizeof(D_buffer));

        mbedtls_mpi_read_binary(&Q, Q_buffer, sizeof(Q_buffer)); 
        mbedtls_mpi_read_binary(&P, P_buffer, sizeof(P_buffer));
        mbedtls_mpi_read_binary(&N, N_buffer, sizeof(N_buffer));
        mbedtls_mpi_read_binary(&D, D_buffer, sizeof(D_buffer));

        import_ret = mbedtls_rsa_import(&rsa, &N, &P, &Q, &D, &E);
        complete_ret = mbedtls_rsa_complete(&rsa);
        key_check_ret = mbedtls_rsa_check_pub_priv(&rsa, &rsa);

        if (import_ret != 0 || complete_ret != 0 || key_check_ret != 0)
        {
            ret = -1;
            break;
        }

        public_ret = mbedtls_rsa_public(&rsa, plain_text, cipher_text);
        private_ret = mbedtls_rsa_private(&rsa, rand, NULL, cipher_text, decrypted_text);

        if (public_ret != 0 || private_ret != 0)
        {
            ret = -1;
            break;
        }
    }
    
    return ret;
}
