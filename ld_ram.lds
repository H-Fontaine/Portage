MEMORY
{
    FLASH (rx) : ORIGIN = 0x00000000, LENGTH = 1M
    SRAM1 (wx) : ORIGIN = 0x20000000, LENGTH = 112K
    SRAM2 (w) : ORIGIN = 0x2001C000, LENGTH = 16K
}

_stack_begin = ORIGIN(SRAM2) + LENGTH(SRAM2);

SECTIONS
{
    /*.boot : {
        *(.boot)
    } > FLASH

    .bootloader : {
        *(.bootloader)
    } > FLASH*/

    .text : {
        *(.text)
    } > SRAM1 /*AT > FLASH*/

    .rodata : {
        *(.rodata)
    } > FLASH

    .data : {
        *(.data)
    } > SRAM1 /*AT > FLASH*/

    .bss : {
        *(.bss) *(COMMON)
    } > SRAM1 /*AT > FLASH*/
}


_text_start_LMA = LOADADDR(.text);
_text_start_VMA = ADDR(.text);
_text_size = SIZEOF(.text);

_data_start_LMA = LOADADDR(.data);
_data_start_VMA = ADDR(.data);
_data_size = SIZEOF(.data);

_bss_start_VMA = ADDR(.bss);
_bss_size = SIZEOF(.bss);

ENTRY(_start)