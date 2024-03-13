.syntax unified
.thumb
.arch armv7-m

.global _start

.section .bootloader
_start :
    ldr sp, =_stack_begin
    bl init
