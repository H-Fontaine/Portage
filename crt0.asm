.syntax unified
.thumb
.arch armv7-m

.global _start

_start :
    ldr sp, =_stack_begin
    bl init
    bl main
    b exit