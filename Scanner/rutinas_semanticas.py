from generador_codigo import emit, siguiente_etiqueta
from clase_pila import Pila
from tabla_simbolos import VariableGlobal, tabla_simbolos

# Variables internas del compilador
tipo_actual = None       # 'int', 'bool', 'char'
id_actual = None
valor_actual = None

pila_etiquetas_if = Pila()
pila_etiquetas_while = Pila()
pila_break = Pila()
pila_continue = Pila()
pila_tipos = Pila()  # Pila paralela para tipos en expresiones

# === Declaración de variables globales ===

def SalveTipoActualInt():
    global tipo_actual
    tipo_actual = 'int'

def SalveTipoActualBool():
    global tipo_actual
    tipo_actual = 'bool'

def SalveTipoActualChr():
    global tipo_actual
    tipo_actual = 'char'

def SalveID(atributos):
    global id_actual
    id_actual = atributos['lexema']

def SalvelitInt(atributos):
    global valor_actual
    valor_actual = atributos['lexema']

def SalvelitBool(atributos):
    global valor_actual
    valor_actual = '1' if atributos['lexema'].lower() == 'on' else '0'

def SalvelitChr(atributos):
    global valor_actual
    valor_actual = f"'{atributos['lexema']}'"

def VarGlobal():
    if id_actual is None or tipo_actual is None:
        raise Exception("Error interno: ID o tipo actual no definido.")

    nombre_asm = f"VG_{id_actual}"
    linea = ""

    if tipo_actual == 'int':
        linea = f"{nombre_asm} dw {valor_actual if valor_actual else '?'}"
    elif tipo_actual == 'bool':
        linea = f"{nombre_asm} db {valor_actual if valor_actual else '?'}"
    elif tipo_actual == 'char':
        linea = f"{nombre_asm} db {valor_actual if valor_actual else '?'}"
    else:
        raise Exception(f"Tipo no soportado: {tipo_actual}")

    emit(linea)
    tabla_simbolos[id_actual] = VariableGlobal(id_actual, tipo_actual)

# === Manejo de expresiones ===

def litnum1(atributos):
    emit(f"mov ax, {atributos['lexema']}")
    emit("push ax")
    pila_tipos.apilar("int")

def RevTipoId(atributos):
    nombre = atributos['lexema']
    if nombre not in tabla_simbolos:
        raise Exception(f"Variable no declarada: {nombre}")
    simbolo = tabla_simbolos[nombre]

    if simbolo.tipo == 'int':
        emit(f"mov ax, VG_{nombre}")
        emit("push ax")
        pila_tipos.apilar("int")
    else:
        raise Exception(f"Acceso a tipo no soportado en expresiones: {simbolo.tipo}")

# === Operaciones aritméticas ===

def gencodmas():
    _op_binaria("add")

def gencodmenos():
    _op_binaria("sub")

def gencodmul():
    _op_binaria("imul")

def gencoddiv():
    tipo2 = pila_tipos.desapilar()
    tipo1 = pila_tipos.desapilar()
    if tipo1 == tipo2 == "int":
        emit("pop bx")
        emit("cmp bx, 0")
        emit("je ERROR_DIV_CERO")
        emit("pop ax")
        emit("xor dx, dx")
        emit("div bx")
        emit("push ax")
        pila_tipos.apilar("int")
    else:
        raise Exception("Tipos incompatibles para división")

def _op_binaria(op):
    tipo2 = pila_tipos.desapilar()
    tipo1 = pila_tipos.desapilar()
    if tipo1 == tipo2 == "int":
        emit("pop bx")
        emit("pop ax")
        emit(f"{op} ax, bx")
        emit("push ax")
        pila_tipos.apilar("int")
    else:
        raise Exception(f"Tipos incompatibles para operación {op}")

# === Comparadores ===

def gencodeq():
    _comparador("je")

def gencodneq():
    _comparador("jne")

def gencodlt():
    _comparador("jl")

def gencodgt():
    _comparador("jg")

def gencodle():
    _comparador("jle")

def gencodge():
    _comparador("jge")

def _comparador(salto):
    tipo2 = pila_tipos.desapilar()
    tipo1 = pila_tipos.desapilar()
    if tipo1 == tipo2 == "int":
        emit("pop bx")
        emit("pop ax")
        emit("cmp ax, bx")
        etiqueta = siguiente_etiqueta()
        salida = siguiente_etiqueta()
        emit(f"{salto} {etiqueta}")
        emit("push 0")
        emit(f"jmp {salida}")
        emit(f"{etiqueta}:")
        emit("push 1")
        emit(f"{salida}:")
        pila_tipos.apilar("int")
    else:
        raise Exception("Comparación no válida entre tipos")

# === Instrucción halt ===

def halt1():
    tipo = pila_tipos.desapilar()
    if tipo != "int":
        emit("; Conversión a entero no implementada (string/fraction/etc.)")
    emit("pop ax")
    emit("mov ah, 4Ch")
    emit("int 21h")

# === Instrucción if ===

def if1():
    emit("pop ax")
    emit("cmp ax, 0")
    et_else = siguiente_etiqueta()
    emit(f"je {et_else}")
    pila_etiquetas_if.apilar(et_else)

def if2():
    et_else = pila_etiquetas_if.desapilar()
    et_end = siguiente_etiqueta()
    emit(f"jmp {et_end}")
    emit(f"{et_else}:")
    pila_etiquetas_if.apilar(et_end)

def if3():
    et_end = pila_etiquetas_if.desapilar()
    emit(f"{et_end}:")

# === Instrucción while ===

def while1():
    et_inicio = siguiente_etiqueta()
    emit(f"{et_inicio}:")
    pila_etiquetas_while.apilar(et_inicio)
    pila_continue.apilar(et_inicio)

def while2():
    emit("pop ax")
    emit("cmp ax, 0")
    et_bloque = siguiente_etiqueta()
    et_salida = siguiente_etiqueta()
    emit(f"jne {et_bloque}")
    emit(f"jmp {et_salida}")
    emit(f"{et_bloque}:")
    pila_etiquetas_while.apilar(et_salida)
    pila_break.apilar(et_salida)

def while3():
    et_salida = pila_etiquetas_while.desapilar()
    et_inicio = pila_etiquetas_while.desapilar()
    emit(f"jmp {et_inicio}")
    emit(f"{et_salida}:")
    pila_break.desapilar()
    pila_continue.desapilar()

# === Instrucciones break y continue ===

def break1():
    if pila_break.esta_vacia():
        raise Exception("break fuera de ciclo")
    et_salida = pila_break.tope()
    emit(f"jmp {et_salida}")

def continue1():
    if pila_continue.esta_vacia():
        raise Exception("continue fuera de ciclo")
    et_inicio = pila_continue.tope()
    emit(f"jmp {et_inicio}")

# === Asignación: Z := X + 1; ===

def assign1(atributos):
    nombre = atributos['lexema']
    tipo = pila_tipos.desapilar()
    if tipo != "int":
        raise Exception("Asignación solo soporta enteros")
    emit("pop ax")
    emit(f"mov VG_{nombre}, ax")

# === Impresión ===

def print1():
    tipo = pila_tipos.tope()
    if tipo == "int":
        emit("call printInt")
    else:
        emit("; print de tipo no implementado aún")

def print2():
    emit("call printNL")
