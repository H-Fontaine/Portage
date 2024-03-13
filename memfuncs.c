#include <stdint.h>
#include <stddef.h>
#include "memfuncs.h"

void * memcpy(void * dest, const void * src, size_t size) {
    uint8_t* destination = (uint8_t*)dest;
    uint8_t* source = (uint8_t*)src;
    for (size_t i = 0; i < size; i++)
    {
        *(destination++) = *(source++);
    }
    return dest;
}

void* memmove(void* dest, const void* src, size_t size) {
    uint8_t* destination = (uint8_t*)dest;
    uint8_t* source = (uint8_t*)src;
    if (destination > source)
    {
        for (size_t i = 0; i < size; i++)
        {
            *(destination + size - i) = *(source + size - i);
        }
    } else {
        for (size_t i = 0; i < size; i++)
        {
            *(destination + i) = *(source + i);
        }
    }
    return dest;    
}


void * memset (void * ptr, int value, size_t size) {
    unsigned char val = (unsigned char) value;
    for (size_t i = 0; i < size; i++)
    {
        *((unsigned char*)ptr + i) = val;
    }
    return ptr;
}
 
int memcmp (const void * ptr1, const void * ptr2, size_t size) {
    unsigned char* block_1 = (unsigned char*) ptr1;
    unsigned char* block_2 = (unsigned char*) ptr2;
    for (size_t i = 0; i < size; i++)
    {
        if (*(block_1 + i) < *(block_2 + i))
        {
            return -1;
        } else if (*(block_1 + i) > *(block_2 + i))
        {
            return 1;
        }        
    }
    return 0;
}

int strlen(const char * str) {
    int len = 0;
    while (*(str + len) != '\0')
    {
        len++;
    }
    return len;
}


int snprintf(char * str, size_t size, const char * format, ...) {
    //TODO: Implement snprintf
    return 0;
}