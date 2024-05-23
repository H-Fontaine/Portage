#include "mbedtls/rsa.h"
#include "mbedtls_dependencies.h"

#define WINDOW_SIZE ((size_t) 1 << MBEDTLS_MPI_WINDOW_SIZE)

extern int mpi_select(mbedtls_mpi *R, const mbedtls_mpi *T, size_t T_size, size_t idx);



int user_defined_wrapper() {
    mbedtls_mpi W[WINDOW_SIZE];
    mbedtls_mpi result;
    mbedtls_mpi_init(&result);
    
    memset(W, 0, sizeof(W));
    for (size_t i = 0; i < WINDOW_SIZE; i++) {
        mbedtls_mpi_init(&W[i]);
    }

    const unsigned char m2_buffer[1024 / 8]; //vérifier taille buffer
    const unsigned char m3_buffer[1024 / 8]; 

    memset((void*)m2_buffer, 0, sizeof(m2_buffer));
    memset((void*)m3_buffer, 0, sizeof(m3_buffer));

    mbedtls_mpi_read_binary(&W[2], m2_buffer, sizeof(m2_buffer));
    mbedtls_mpi_read_binary(&W[3], m3_buffer, sizeof(m3_buffer));

    size_t idx = 0;
    mpi_select(&result, W, WINDOW_SIZE, idx);

    return 0;
}