# parser.py

from scanner import TokenType

# ---------------------------------------------------
# 2.1. Definición de terminales y no terminales
# ---------------------------------------------------

# Cada TokenType mapea a un índice único [0 .. NUM_T-1]
TERMINALES = {
    TokenType.ANVIL:       0,
    TokenType.BEDROCK:     1,
    TokenType.BOOK:        2,
    TokenType.CRAFTINGTABLE: 3,
    TokenType.CHEST:       4,
    TokenType.ENTITY:      5,
    TokenType.GHAST:       6,
    TokenType.INVENTORY:   7,
    TokenType.OBSIDIAN:    8,
    TokenType.POLLOCRUDO:  9,
    TokenType.POLLOASADO:  10,
    TokenType.RESOURCEPACK: 11,
    TokenType.RECIPE:      12,
    TokenType.RUNE:        13,
    TokenType.REPEATER:    14,
    TokenType.SPAWNPOINT:  15,
    TokenType.STACK:       16,
    TokenType.SPIDER:      17,
    TokenType.SHELF:       18,
    TokenType.TORCH:       19,
    TokenType.WORLDNAME:   20,
    TokenType.WORLDSAVE:   21,
    TokenType.BOOL_ON:     22,
    TokenType.BOOL_OFF:    23,
    TokenType.IS:          24,
    TokenType.ISNOT:       25,
    TokenType.ID:          26,
    TokenType.INT_LIT:     27,
    TokenType.FLOAT_LIT:   28,
    TokenType.CHAR_LIT:    29,
    TokenType.STRING_LIT:  30,
    TokenType.LPAREN:      31,
    TokenType.RPAREN:      32,
    TokenType.LBRACE:      33,
    TokenType.RBRACE:      34,
    TokenType.LBRACKET:    35,
    TokenType.RBRACKET:    36,
    TokenType.SEMICOLON:   37,
    TokenType.COLON:       38,
    TokenType.DOT:         39,
    TokenType.COMMA:       40,
    TokenType.AT:          41,
    TokenType.PLUS:        42,
    TokenType.MINUS:       43,
    TokenType.MULTIPLY:    44,
    TokenType.DIVIDE:      45,   # '//'  
    TokenType.FLOAT_OP:    46,   # ':+', ':-', ':*', '://', ':%'
    TokenType.MODULO:      47,
    TokenType.LT:          48,
    TokenType.GT:          49,
    TokenType.LE:          50,
    TokenType.GE:          51,
    TokenType.EQ:          52,
    TokenType.NE:          53,
    TokenType.COMMENT:     54,
    TokenType.EOF:         55,
    TokenType.ERROR:       56,   # (No se usa como token válido en el parser)
}

NUM_T = len(TERMINALES)

# Para simplificar, enumeramos los no terminales con índices [0 .. NUM_NT-1].

NO_TERMINALES = {
    'S':  0,
    'WorldDecl':  1,
    'StmtList':   2,
    'Stmt':       3,
    'Expr':       4,
    # falta el resto de la gramatica
}

NUM_NT = len(NO_TERMINALES)

OFFSET_T = NUM_NT

# Tabla de Parsing (TP) y Tabla de Lados Derechos (TLD)

TP = [[-1] * NUM_T for _ in range(NUM_NT)]

TLD = [
    # Regla 0: S ::= WorldDecl StmtList
    [ NO_TERMINALES['WorldDecl'], NO_TERMINALES['StmtList'] ],

    # Regla 1: WorldDecl ::= 'WorldName' ID ':' '{' StmtList '}' 
    [ OFFSET_T + TERMINALES[TokenType.WORLDNAME],
      OFFSET_T + TERMINALES[TokenType.ID],
      OFFSET_T + TERMINALES[TokenType.COLON],
      OFFSET_T + TERMINALES[TokenType.LBRACE],
      NO_TERMINALES['StmtList'],
      OFFSET_T + TERMINALES[TokenType.RBRACE]
    ],

    # Regla 2: StmtList ::= Stmt StmtList | ε
    [ NO_TERMINALES['Stmt'], NO_TERMINALES['StmtList'] ],
    [ -2 ],  # epsilon

    # Regla 3: Stmt ::= Expr ';'
    [ NO_TERMINALES['Expr'], OFFSET_T + TERMINALES[TokenType.SEMICOLON] ],

    # Regla 4: Expr ::= ID '=' Expr
    [ OFFSET_T + TERMINALES[TokenType.ID],
      OFFSET_T + TERMINALES[TokenType.ASSIGN],
      NO_TERMINALES['Expr']
    ],

    #modo de ejemplo porque falta la gramatica completa
]


TP[ NO_TERMINALES['S']       ][ TERMINALES[TokenType.WORLDNAME] ] = 0
TP[ NO_TERMINALES['WorldDecl'] ][ TERMINALES[TokenType.WORLDNAME] ] = 1
TP[ NO_TERMINALES['StmtList']   ][ TERMINALES[TokenType.ANVIL] ]   = 2
TP[ NO_TERMINALES['StmtList']   ][ TERMINALES[TokenType.ID] ]      = 2
TP[ NO_TERMINALES['StmtList']   ][ TERMINALES[TokenType.SEMICOLON] ] = 3  # Regla 2: ε (supongamos que en el Follow de StmtList está ';')
TP[ NO_TERMINALES['Stmt']     ][ TERMINALES[TokenType.ID] ]      = 3
TP[ NO_TERMINALES['Expr']     ][ TERMINALES[TokenType.ID] ]      = 4

# modo de ejemplo porque falta la gramatica completa

# Flujo de tokens (TokenStream) -------

class TokenStream:
    """
    Envuelve la lista de tokens obtenidos en la fase léxica,
    proporciona peek() y next() para que el parser los consuma.
    """
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        # Devuelve el token actual sin consumirlo
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        # Si nos pasamos, devolvemos un EOF ficticio
        return self.tokens[-1]

    def next(self):
        # Consume y retorna el token actual
        if self.pos < len(self.tokens):
            t = self.tokens[self.pos]
            self.pos += 1
            return t
        return self.tokens[-1]


# Recuperación de errores --------

def recover_on_error(ts: TokenStream):
    """
    Avanza en el TokenStream hasta encontrar un ';', '}', o EOF. Luego regresa.
    """
    print("  [Re-sincronizando: buscando ';' o fin de bloque…]")
    while True:
        tok = ts.next()
        if tok.type in (TokenType.SEMICOLON, TokenType.RBRACE, TokenType.EOF):
            print(f"  [Re-sincronizado en token {tok.type.name}]")
            return

# Driver principal de parsing ----------

def parse_tokens(tokens):
    """
    Recibe la lista completa de tokens (fase léxica ya terminada),
    y realiza el análisis sintáctico dirigido por tabla LL(1).
    Devuelve una lista de cadenas con los mensajes de error sintáctico (vacía si no hay).
    """
    ts = TokenStream(tokens)
    errores = []

    # Inicializo TA (token actual) sacado del TokenStream:
    TA = ts.peek()

    # Creo mi pila de parsing y pongo en el tope el símbolo inicial (por ejemplo 'S')
    pila = Stack()
    pila.push(SIMBOLO_INICIAL)

    # Mientras la pila no esté vacía:
    while not pila.is_empty():
        EAP = pila.pop()

        # CASO A: EAP es un terminal (EAP >= OFFSET_T)
        if EAP >= OFFSET_T:
            terminal_index = EAP - OFFSET_T
            # Buscamos qué TokenType corresponde a ese índice
            #   Invertimos el diccionario TERMINALES:
            expected_tok = None
            for tokype, idx in TERMINALES.items():
                if idx == terminal_index:
                    expected_tok = tokype
                    break

            if expected_tok is None:
                errores.append(f"[INTERNAL] Símbolo terminal desconocido: código {EAP}")
                return errores

            # Comparamos TA.type con expected_tok:
            if TA.type == expected_tok:
                # Hicimos match, consumimos el token y seguimos
                TA = ts.next()
            else:
                errores.append(
                    f"Error sintáctico: esperaba {expected_tok.name} "
                    f"pero vino {TA.type.name} (lexema '{TA.lexeme}') en línea {TA.line}"
                )
                # Recuperación de error: re-sincronizar
                recover_on_error(ts)
                TA = ts.peek()
            continue

        # CASO B: EAP es un no terminal (0 <= EAP < NUM_NT)
        fila = EAP
        # obtenemos la columna correspondiente al token TA
        col = TERMINALES.get(TA.type, None)
        if col is None:
            # Si TA.type no está en TERMINALES, error
            errores.append(
                f"Error sintáctico: token inesperado {TA.type.name} "
                f"(lexema '{TA.lexeme}') en línea {TA.line}"
            )
            recover_on_error(ts)
            TA = ts.peek()
            continue

        regla = TP[fila][col]
        if regla < 0:
            nt_name = None
            for name, idx in NO_TERMINALES.items():
                if idx == fila:
                    nt_name = name
                    break
            errores.append(
                f"Error sintáctico en no terminal '{nt_name}': "
                f"entrada '{TA.type.name}' (lexema '{TA.lexeme}') no está en PREDICT"
            )
            recover_on_error(ts)
            TA = ts.peek()
            continue

        # Si hay una regla válida, obtengo su lado derecho y la empujo en orden inverso
        derecho = TLD[regla]
        # Si la producción es [ -2 ] (epsilon), NO empujamos nada
        if not (len(derecho)==1 and derecho[0] == -2):
            for simbolo in reversed(derecho):
                pila.push(simbolo)

        # NOTA: no consumimos TA en este punto; sólo avanzamos cuando hagamos match del terminal.


    # Al salir del while, la pila quedó vacía. Debemos verificar que TA sea EOF.
    if TA.type != TokenType.EOF:
        errores.append(
            f"Error sintáctico: entrada no consumida al terminar el parser. "
            f"Token sobrante: {TA.type.name} (lexema '{TA.lexeme}') en línea {TA.line}"
        )
    else:
        # Si no hubo errores durante todo el proceso, informamos éxito
        errores.append("SIN_ERRORES")

    return errores


# Clase de la pila

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
