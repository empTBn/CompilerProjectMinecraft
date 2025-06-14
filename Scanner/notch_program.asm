; ---------------------------------------------
; Archivo generado automáticamente por Notch Engine Compiler
; ---------------------------------------------

pila segment stack 'stack'
    dw 4096 dup(?)
pila ends

datos segment para public
    include pool_literales.plt

    ; Aquí irán las variables globales generadas automáticamente

datos ends

codigo segment para public
    assume cs:codigo, ds:datos, ss:pila

    include runtime.asm

inicio:
    ; Aquí comienza el programa principal

    ; El compilador generará el código ensamblador aquí

codigo ends
end inicio
