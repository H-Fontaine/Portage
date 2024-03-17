#include "mbedtls/rsa.h"
#include "mbedtls_dependencies.h"
#include "mbedtls/memory_buffer_alloc.h"

#define HEAP_SIZE_IN_BYTES 16000

unsigned char memory_buf[HEAP_SIZE_IN_BYTES];

int main() {
    mbedtls_memory_buffer_alloc_init(memory_buf, sizeof(memory_buf));

    int ret = 1;
    
    mbedtls_rsa_context rsa;
    mbedtls_rsa_init(&rsa);

    mbedtls_mpi E, P, Q;
    mbedtls_mpi_init(&E); mbedtls_mpi_init(&P); mbedtls_mpi_init(&Q);

    mbedtls_mpi_lset(&Q, 792671947);
    mbedtls_mpi_lset(&P, 812954609);
    mbedtls_mpi_lset(&E, 5); //Can't be 3, don't know why

    if ((ret = mbedtls_rsa_import(&rsa, NULL, &P, &Q, NULL, &E)) != 0) {
        //printf(" failed\n  ! mbedtls_rsa_import returned %d\n\n", ret);
        return -1;
    }
    if ((ret = mbedtls_rsa_complete(&rsa)) != 0) {
        //printf(" failed\n  ! mbedtls_rsa_complete returned %d\n\n", ret);
        return -1;
    }

    const size_t modlen = mbedtls_rsa_get_len(&rsa);
    unsigned char plain_text[modlen]; memset(plain_text, 0, sizeof(plain_text)); plain_text[0] = 0;
    unsigned char cipher_text[modlen]; memset(cipher_text, 0, sizeof(cipher_text));
    unsigned char result[modlen]; memset(result, 0, sizeof(result));

    const size_t ilen = 5;
    plain_text[modlen - 5] = 'a';
    plain_text[modlen - 4] = 'b';
    plain_text[modlen - 3] = 'c';
    plain_text[modlen - 2] = 'd';
    plain_text[modlen - 1] = 'e';

    ret = mbedtls_rsa_public(&rsa, plain_text, cipher_text);
    if (ret != 0) {
        //printf(" failed\n  ! mbedtls_rsa_public returned %d\n\n", ret);
        return -1;
    }

    ret = mbedtls_rsa_private(&rsa, rand, NULL, cipher_text, result);
    if (ret != 0) {
        //printf(" failed\n  ! mbedtls_rsa_private returned %d\n\n", ret);
        return -1;
    }
    
    char a, b, c, d, e =0;
    a = result[modlen - ilen];
    b = result[modlen - ilen + 1];
    c = result[modlen - ilen + 2];
    d = result[modlen - ilen + 3];
    e = result[modlen - ilen + 4];
    
    if (a != 'a' || b != 'b' || c != 'c' || d != 'd' || e != 'e') {
        //printf(" failed\n  ! mbedtls_rsa_private returned %d\n\n", ret);
        return -1;
    }
    return 0;
}
