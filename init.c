#include <stdint.h>
#include "mbedtls_dependencies.h"

extern char _text_start_LMA, _text_start_VMA, _text_size, _data_start_LMA, _data_start_VMA, _data_size, /*_vector_start_LMA, _vector_start_VMA, _vector_size,*/ _bss_start_VMA, _bss_size, _stack_begin, _start;

int main(void);

void exit(void) {
    while (1)
    {
        /* code */
    }
}

__attribute__((section(".bootloader"))) void init() {
    memcpy(&_data_start_VMA, &_data_start_LMA, (size_t) &_data_size); //init .data
    memset(&_bss_start_VMA, 0, (size_t) &_bss_size); //init .bss

    main();
    exit();
}

void* const boot[] __attribute__((section(".boot"))) = {
    &_stack_begin, //Stack pointer
    &_start, //Reset vector
};