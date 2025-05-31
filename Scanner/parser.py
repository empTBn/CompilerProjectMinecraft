from scanner import InicializarScanner, DemeToken, TomeToken, FinalizarScanner, TokenType


TERMINALES = {
    TokenType.ANVIL:       0,
    TokenType.ID:          1,
    # … sigue con todos los terminales …
    TokenType.EOF:         99,
}

NO_TERMINALES = {
    'S': 0,
    'A': 1,
    # … etc …
}

SIMBOLO_INICIAL = NO_TERMINALES['S']

NUM_T = len(TERMINALES)
NUM_NT = len(NO_TERMINALES)

# Tabla de Parsing: filas = no terminales, columnas = terminales
# Inicialmente todos -1; luego se rellenará con los números de producción.
TP = [[-1] * NUM_T for _ in range(NUM_NT)]

# Tabla de Lados Derechos: lista de reglas. Cada regla es una lista de símbolos
TLD = [
    # [ ... ],
    # [ ... ],
]


# Utilidades de pila

class Stack:
    def __init__(self):
        self._data = []
    def push(self, x):
        self._data.append(x)
    def pop(self):
        return self._data.pop() if self._data else None
    def top(self):
        return self._data[-1] if self._data else None
    def is_empty(self):
        return not self._data

# Rutinas de re-sincronización (error recovery)

def recover_on_error():
    print("  [Re-sincronizando: buscando ';' o fin de bloque…]")
    while True:
        tok = DemeToken()
        if tok.type in (TokenType.SEMICOLON, TokenType.RBRACE, TokenType.EOF):
            print(f"  [Re-sincronizado en token {tok.type.name}]")
            return
        TomeToken()

# Driver del parser

def parse():
    # Inicializar scanner y leer el primer token
    TA = DemeToken()
    
    # Crear pila y poner el símbolo inicial
    pila = Stack()
    pila.push(SIMBOLO_INICIAL)
    
    # Mientras queden símbolos por procesar
    while not pila.is_empty():
        EAP = pila.pop()  # elemento actual de trabajo
        
        # Caso 1: es un terminal
        if EAP >= NUM_NT:
            # lo comparamos con TA
            # convertimos EAP a TokenType
            expected_tok = list(TERMINALES.keys())[list(TERMINALES.values()).index(EAP)]
            if TA.type == expected_tok:
                TA = DemeToken()
            else:
                print(f"Error sintáctico: esperaba {expected_tok.name} pero vino {TA.type.name}")
                recover_on_error()
                TA = DemeToken()
            continue
        
        # Caso 2: es un no terminal
        fila = EAP
        col  = TERMINALES.get(TA.type, None)
        regla = TP[fila][col] if col is not None else -1
        
        if regla < 0:
            print(f"Error sintáctico en no terminal {list(NO_TERMINALES.keys())[list(NO_TERMINALES.values()).index(EAP)]} con entrada {TA.type.name}")
            recover_on_error()
            TA = DemeToken()
            continue
        # Si hay regla válida, empujar su lado derecho (en orden inverso)
        for simbolo in reversed(TLD[regla]):
            # ignoramos epsilón (que podríamos codificar como -2)
            if simbolo != -2:
                pila.push(simbolo)
    
    # Al final, si TA no es EOF, error
    if TA.type != TokenType.EOF:
        print("Error sintáctico: entrada no consumida al terminar el parser.")
    else:
        print("Análisis sintáctico completado!")