LC0:
    .ascii "Hello World\0"
    .text
.globl strlen
strlen:
    xorq rax,rax
    xorq rcx,rcx
    dec rcx
    repnz scasb
    inc rcx
    not rcx
    movq rcx,rax
    ret