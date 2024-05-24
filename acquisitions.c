#include "mbedtls/rsa.h"
#include "mbedtls_dependencies.h"

#define TABLE_SIZE ((size_t) 1 << MBEDTLS_MPI_WINDOW_SIZE)

extern int mpi_select(mbedtls_mpi *R, const mbedtls_mpi *T, size_t T_size, size_t idx);

extern void trigger_high(uint8_t);
extern void trigger_low(uint8_t);

int user_defined_wrapper() {
    int ret = 0;
    mbedtls_mpi W[TABLE_SIZE];
    mbedtls_mpi result;
    mbedtls_mpi_init(&result);
    
    memset(W, 0, sizeof(W));
    for (size_t i = 0; i < TABLE_SIZE; i++) {
        mbedtls_mpi_init(&W[i]);
    }

    const unsigned char m1_buffer[1024 / 8];
    const unsigned char m2_buffer[1024 / 8];
    const unsigned char m3_buffer[1024 / 8]; 
    
    volatile size_t idx = 0;
    memset((void*)m1_buffer, 0, sizeof(m1_buffer));
    memset((void*)m2_buffer, 0, sizeof(m2_buffer));
    memset((void*)m3_buffer, 0, sizeof(m3_buffer));

    ret = mbedtls_mpi_read_binary(&W[1], m1_buffer, sizeof(m1_buffer));
    ret = mbedtls_mpi_read_binary(&W[2], m2_buffer, sizeof(m2_buffer));
    ret = mbedtls_mpi_read_binary(&W[3], m3_buffer, sizeof(m3_buffer));
    
    
    for (int j = 0; j < 16; j++) {
        trigger_high(15);
        ret = mpi_select(&result, W, TABLE_SIZE, idx);
        trigger_low(15);
    }

    for (size_t i = 0; i < TABLE_SIZE; i++) {
        mbedtls_mpi_free(&W[i]);
    }
    mbedtls_mpi_free(&result);

    return ret;
}