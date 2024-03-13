#ifndef MEMFUNCS_H
#define MEMEFUNCS_H

#include <stdint.h>
#include <stddef.h>

//Copy size bytes from src to dest, return dest
void * memcpy(void * dest, const void * src, size_t size) ;

//Move size bytes from src to dest, handel overlap, return dest
void* memmove(void* dest, const void* src, size_t size) ;

//Set size bytes from ptr at value, return ptr.
void * memset (void * ptr, int value, size_t size) ;

//Compare size bytes at ptr1 and ptr2, return :
//    0, if bytes are all the same
//    1, if the first bytes to be different implies that the byte from prt1 is greater than the byte from ptr2
//   -1, otherwise
int memcmp (const void * ptr1, const void * ptr2, size_t size);

#endif