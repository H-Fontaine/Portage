#ifndef MBEDTLS_DEPENDENCIES_H
#define MBEDTLS_DEPENDENCIES_H

#include <stddef.h>

/*Randomness generator function for blinding*/
int rand(void* a , unsigned char* b, size_t c);

/*strlen for mbedtls_mpi_read_string line 525 in bignum.c*/
unsigned int strlen(const char * str);

// Memory functions
void * memcpy(void * dest, const void * src, size_t size);
void* memmove(void* dest, const void* src, size_t size);
void * memset (void * ptr, int value, size_t size);
int memcmp (const void * ptr1, const void * ptr2, size_t size);

#endif //MBEDTLS_DEPENDENCIES_H