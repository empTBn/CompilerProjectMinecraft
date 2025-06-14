from clase_pila import Pila

archivo_salida = None
contador_etiquetas = 0

# Pilas para control de flujo
pila_if = Pila()
pila_while = Pila()
pila_break = Pila()
pila_continue = Pila()

def crear_archivo_salida(nombre="notch_program.asm"):
    global archivo_salida, contador_etiquetas
    contador_etiquetas = 0
    archivo_salida = open(nombre, "w", encoding="utf-8")

    # Escribir encabezado ASM
    emit("; Código generado automáticamente por el compilador Notch Engine")
    emit("")
    emit("pila segment stack 'stack'")
    emit("  dw 4096 dup(?)")
    emit("pila ends")
    emit("")
    emit("datos segment para public")
    emit("  ; variables globales aquí")
    emit("datos ends")
    emit("")
    emit("codigo segment")
    emit("  assume cs:codigo, ds:datos, ss:pila")
    emit("  include runtime.asm")
    emit("")

def cerrar_archivo():
    if archivo_salida:
        emit("")
        emit("codigo ends")
        emit("end inicio")  # 'inicio' puede cambiar si usas otra etiqueta
        archivo_salida.close()

def emit(linea):
    if archivo_salida:
        archivo_salida.write(linea + "\n")

def siguiente_etiqueta():
    global contador_etiquetas
    etiqueta = f"Et{contador_etiquetas:05}"
    contador_etiquetas += 1
    return etiqueta

# ======= Instrucciones de control =======

def gen_if1():
    emit("pop ax")
    emit("cmp ax, 0")
    et_else = siguiente_etiqueta()
    emit(f"je {et_else}")
    pila_if.apilar(et_else)

def gen_if2():
    et_salir = siguiente_etiqueta()
    emit(f"jmp {et_salir}")
    et_else = pila_if.desapilar()
    emit(f"{et_else}:")
    pila_if.apilar(et_salir)

def gen_if3():
    et_salir = pila_if.desapilar()
    emit(f"{et_salir}:")

def gen_while1():
    et_ciclo = siguiente_etiqueta()
    emit(f"{et_ciclo}:")
    pila_while.apilar(et_ciclo)
    pila_continue.apilar(et_ciclo)

def gen_while2():
    emit("pop ax")
    emit("cmp ax, 0")
    et_bloque = siguiente_etiqueta()
    et_salir = siguiente_etiqueta()
    emit(f"jne {et_bloque}")
    emit(f"jmp {et_salir}")
    emit(f"{et_bloque}:")
    pila_while.apilar(et_salir)
    pila_break.apilar(et_salir)

def gen_while3():
    et_salir = pila_while.desapilar()
    et_ciclo = pila_while.desapilar()
    emit(f"jmp {et_ciclo}")
    emit(f"{et_salir}:")
    pila_break.desapilar()
    pila_continue.desapilar()

def gen_break():
    et = pila_break.tope()
    emit(f"jmp {et}")

def gen_continue():
    et = pila_continue.tope()
    emit(f"jmp {et}")

def gen_halt():
    # En proyectos futuros se agregan conversiones de tipo antes del halt
    emit("pop ax")
    emit("mov ah, 4Ch")
    emit("int 21h")
