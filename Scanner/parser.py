from scanner import TokenType

# Mapeo de terminales a índices 

TERMINALES = {
    TokenType.ANVIL:        0,
    TokenType.BEDROCK:      1,
    TokenType.BOOK:         2,
    TokenType.CRAFTINGTABLE:3,
    TokenType.CHEST:        4,
    TokenType.ENTITY:       5,
    TokenType.GHAST:        6,
    TokenType.INVENTORY:    7,
    TokenType.OBSIDIAN:     8,
    TokenType.POLLOCRUDO:   9,
    TokenType.POLLOASADO:   10,
    TokenType.RESOURCEPACK: 11,
    TokenType.RECIPE:       12,
    TokenType.RUNE:         13,
    TokenType.REPEATER:     14,
    TokenType.SPAWNPOINT:   15,
    TokenType.STACK:        16,
    TokenType.SPIDER:       17,
    TokenType.SHELF:        18,
    TokenType.TORCH:        19,
    TokenType.WORLDNAME:    20,
    TokenType.WORLDSAVE:    21,
    TokenType.BOOL_ON:      22,
    TokenType.BOOL_OFF:     23,
    TokenType.IS:           24,    # no usado en la gramática provisional
    TokenType.ISNOT:        25,    # no usado en la gramática provisional
    TokenType.ID:           26,
    TokenType.INT_LIT:      27,
    TokenType.FLOAT_LIT:    28,    # no usado aquí
    TokenType.CHAR_LIT:     29,    # no usado aquí
    TokenType.STRING_LIT:   30,
    TokenType.LPAREN:       31,
    TokenType.RPAREN:       32,
    TokenType.LBRACE:       33,
    TokenType.RBRACE:       34,
    TokenType.LBRACKET:     35,    # no usado aquí
    TokenType.RBRACKET:     36,    # no usado aquí
    TokenType.SEMICOLON:    37,
    TokenType.COLON:        38,
    TokenType.DOT:          39,    # no usado aquí
    TokenType.COMMA:        40,
    TokenType.AT:           41,    # no usado aquí
    TokenType.PLUS:         42,    # no usado aquí
    TokenType.MINUS:        43,    # no usado aquí
    TokenType.MULTIPLY:     44,    # no usado aquí
    TokenType.DIVIDE:       45,    # no usado aquí
    TokenType.FLOAT_OP:     46,    # no usado aquí
    TokenType.MODULO:       47,    # no usado aquí
    TokenType.LT:           48,    # no usado aquí
    TokenType.GT:           49,    # no usado aquí
    TokenType.LE:           50,    # no usado aquí
    TokenType.GE:           51,    # no usado aquí
    TokenType.EQ:           52,    # no usado aquí
    TokenType.NE:           53,    # no usado aquí
    TokenType.COMMENT:      54,    # no se usa en el parser, se descarta
    TokenType.EOF:          55,
    TokenType.ERROR:        56,    # No se trata como token válido de parser
}

NUM_T = len(TERMINALES)

# No terminales 

NO_TERMINALES = {
    'S':           0,
    'WorldDecl':   1,
    'StmtList':    2,
    'Stmt':        3,
    'EntityCall':  4,
    'Assignment':  5,
    'Expr':        6,
    'ArgList':     7,
    'MoreArgs':    8,
    'Toggle':      9,
    'RepeatStmt':  10,
}

NUM_NT = len(NO_TERMINALES)

EPSILON = -2

# Cuando empujamos un terminal en la pila, en realidad lo codificamos
# como (OFFSET_T + índice_en_TERMINALES). Para distinguir terminales vs. no terminales:
OFFSET_T = NUM_NT

# Tabla de Lados Derechos (TLD)

TLD = [
    # Regla 0: S ::= WorldDecl
    [ NO_TERMINALES['WorldDecl'] ],

    # Regla 1: WorldDecl ::= WORLDNAME ID COLON LBRACE StmtList RBRACE
    [
      OFFSET_T + TERMINALES[TokenType.WORLDNAME],
      OFFSET_T + TERMINALES[TokenType.ID],
      OFFSET_T + TERMINALES[TokenType.COLON],
      OFFSET_T + TERMINALES[TokenType.LBRACE],
      NO_TERMINALES['StmtList'],
      OFFSET_T + TERMINALES[TokenType.RBRACE]
    ],

    # Regla 2: StmtList ::= Stmt StmtList
    [ NO_TERMINALES['Stmt'], NO_TERMINALES['StmtList'] ],

    # Regla 3: StmtList ::= ε
    [ EPSILON ],

    # Regla 4: Stmt ::= EntityCall SEMICOLON
    [
      NO_TERMINALES['EntityCall'],
      OFFSET_T + TERMINALES[TokenType.SEMICOLON]
    ],

    # Regla 5: Stmt ::= Assignment SEMICOLON
    [
      NO_TERMINALES['Assignment'],
      OFFSET_T + TERMINALES[TokenType.SEMICOLON]
    ],

    # Regla 6: Stmt ::= Toggle SEMICOLON
    [
      NO_TERMINALES['Toggle'],
      OFFSET_T + TERMINALES[TokenType.SEMICOLON]
    ],

    # Regla 7: Stmt ::= RepeatStmt
    [ NO_TERMINALES['RepeatStmt'] ],

    # Regla 8: EntityCall ::= (ANVIL | BEDROCK | ... | TORCH | WORLDSAVE) LPAREN ArgList RPAREN
    # Para simplificar, manejamos todas estas 18 “palabras reservadas” como posibles
    # primeros símbolos. En la tabla TP se pondrá la misma producción 8 para cada uno.
    [
      # (usaremos el TokenType valor para decidir cuál poner)
      # El parser dirá “si TA.type es ANVIL, o BEDROCK, ..., aplica la Regla 8”
      # Luego empujaremos estos tres símbolos:
      OFFSET_T + TERMINALES[TokenType.ANVIL],        # <- se sobrescribirá en TP para cada keyword
      OFFSET_T + TERMINALES[TokenType.LPAREN],
      NO_TERMINALES['ArgList'],
      OFFSET_T + TERMINALES[TokenType.RPAREN]
    ],

    # Regla 9: Assignment ::= ID ASSIGN Expr
    [
      OFFSET_T + TERMINALES[TokenType.ID],
      OFFSET_T + TERMINALES[TokenType.ASSIGN],
      NO_TERMINALES['Expr']
    ],

    # Regla 10: Expr ::= ID
    [ OFFSET_T + TERMINALES[TokenType.ID] ],

    # Regla 11: Expr ::= INT_LIT
    [ OFFSET_T + TERMINALES[TokenType.INT_LIT] ],

    # Regla 12: Expr ::= STRING_LIT
    [ OFFSET_T + TERMINALES[TokenType.STRING_LIT] ],

    # Regla 13: Toggle ::= BOOL_ON LPAREN ID RPAREN
    [
      OFFSET_T + TERMINALES[TokenType.BOOL_ON],
      OFFSET_T + TERMINALES[TokenType.LPAREN],
      OFFSET_T + TERMINALES[TokenType.ID],
      OFFSET_T + TERMINALES[TokenType.RPAREN]
    ],

    # Regla 14: Toggle ::= BOOL_OFF LPAREN ID RPAREN
    [
      OFFSET_T + TERMINALES[TokenType.BOOL_OFF],
      OFFSET_T + TERMINALES[TokenType.LPAREN],
      OFFSET_T + TERMINALES[TokenType.ID],
      OFFSET_T + TERMINALES[TokenType.RPAREN]
    ],

    # Regla 15: RepeatStmt ::= REPEATER ID ASSIGN Expr LBRACE StmtList RBRACE
    [
      OFFSET_T + TERMINALES[TokenType.REPEATER],
      OFFSET_T + TERMINALES[TokenType.ID],
      OFFSET_T + TERMINALES[TokenType.ASSIGN],
      NO_TERMINALES['Expr'],
      OFFSET_T + TERMINALES[TokenType.LBRACE],
      NO_TERMINALES['StmtList'],
      OFFSET_T + TERMINALES[TokenType.RBRACE]
    ],

    # Regla 16: ArgList ::= Expr MoreArgs
    [ NO_TERMINALES['Expr'], NO_TERMINALES['MoreArgs'] ],

    # Regla 17: ArgList ::= ε
    [ EPSILON ],

    # Regla 18: MoreArgs ::= COMMA Expr MoreArgs
    [
      OFFSET_T + TERMINALES[TokenType.COMMA],
      NO_TERMINALES['Expr'],
      NO_TERMINALES['MoreArgs']
    ],

    # Regla 19: MoreArgs ::= ε
    [ EPSILON ],
]

# Tabla de Parsing (TP): inicializamos todo en -1, luego llenamos

TP = [[-1] * NUM_T for _ in range(NUM_NT)]

# Regla 0: S ::= WorldDecl 
for tokype in [TokenType.WORLDNAME]:
    TP[ NO_TERMINALES['S'] ][ TERMINALES[tokype] ] = 0

# Regla 1: WorldDecl ::= WORLDNAME ID COLON LBRACE StmtList RBRACE
for tokype in [TokenType.WORLDNAME]:
    TP[ NO_TERMINALES['WorldDecl'] ][ TERMINALES[tokype] ] = 1

# Regla 2: StmtList ::= Stmt StmtList   (cuando el primer token de “Stmt” sea alguno de estos)
for first in (
    TokenType.ANVIL, TokenType.BEDROCK, TokenType.BOOK, TokenType.CRAFTINGTABLE,
    TokenType.CHEST, TokenType.ENTITY, TokenType.GHAST, TokenType.INVENTORY,
    TokenType.OBSIDIAN, TokenType.POLLOCRUDO, TokenType.POLLOASADO, TokenType.RESOURCEPACK,
    TokenType.RECIPE, TokenType.RUNE, TokenType.REPEATER, TokenType.SPAWNPOINT,
    TokenType.STACK, TokenType.SPIDER, TokenType.SHELF, TokenType.TORCH,
    TokenType.WORLDSAVE,
    TokenType.ID,
    TokenType.BOOL_ON, TokenType.BOOL_OFF
):
    TP[ NO_TERMINALES['StmtList'] ][ TERMINALES[first] ] = 2

# Regla 3: StmtList ::= ε    (si el próximo token cierra bloque o es RBRACE o EOF)
for t in (TokenType.RBRACE, TokenType.EOF):
    TP[ NO_TERMINALES['StmtList'] ][ TERMINALES[t] ] = 3

# Regla 4: Stmt ::= EntityCall SEMICOLON
#        válido si el TA es alguna de las keywords de entidad:
for first in (
    TokenType.ANVIL, TokenType.BEDROCK, TokenType.BOOK, TokenType.CRAFTINGTABLE,
    TokenType.CHEST, TokenType.ENTITY, TokenType.GHAST, TokenType.INVENTORY,
    TokenType.OBSIDIAN, TokenType.POLLOCRUDO, TokenType.POLLOASADO, TokenType.RESOURCEPACK,
    TokenType.RECIPE, TokenType.RUNE, TokenType.REPEATER, TokenType.SPAWNPOINT,
    TokenType.STACK, TokenType.SPIDER, TokenType.SHELF, TokenType.TORCH, TokenType.WORLDSAVE
):
    TP[ NO_TERMINALES['Stmt'] ][ TERMINALES[first] ] = 4

# Regla 5: Stmt ::= Assignment SEMICOLON    (cuando TA es ID)
TP[ NO_TERMINALES['Stmt'] ][ TERMINALES[TokenType.ID] ] = 5

# Regla 6: Stmt ::= Toggle SEMICOLON        (si TA es BOOL_ON o BOOL_OFF)
TP[ NO_TERMINALES['Stmt'] ][ TERMINALES[TokenType.BOOL_ON] ]  = 6
TP[ NO_TERMINALES['Stmt'] ][ TERMINALES[TokenType.BOOL_OFF] ] = 6

# Regla 7: Stmt ::= RepeatStmt             (si TA es REPEATER)
TP[ NO_TERMINALES['Stmt'] ][ TERMINALES[TokenType.REPEATER] ] = 7

# Regla 8: EntityCall ::= KEYWORD LPAREN ArgList RPAREN
#   (Los “KEYWORD” de entidad se repiten 18 veces, pero apuntan a la misma producción 8)
for kw in (
    TokenType.ANVIL, TokenType.BEDROCK, TokenType.BOOK, TokenType.CRAFTINGTABLE,
    TokenType.CHEST, TokenType.ENTITY, TokenType.GHAST, TokenType.INVENTORY,
    TokenType.OBSIDIAN, TokenType.POLLOCRUDO, TokenType.POLLOASADO, TokenType.RESOURCEPACK,
    TokenType.RECIPE, TokenType.RUNE, TokenType.REPEATER, TokenType.SPAWNPOINT,
    TokenType.STACK, TokenType.SPIDER, TokenType.SHELF, TokenType.TORCH, TokenType.WORLDSAVE
):
    TP[ NO_TERMINALES['EntityCall'] ][ TERMINALES[kw] ] = 8

# Regla 9: Assignment ::= ID ASSIGN Expr   (si TA es ID)
TP[ NO_TERMINALES['Assignment'] ][ TERMINALES[TokenType.ID] ] = 9

# Regla 10: Expr ::= ID                     (si TA es ID)
TP[ NO_TERMINALES['Expr'] ][ TERMINALES[TokenType.ID] ] = 10

# Regla 11: Expr ::= INT_LIT                (si TA es INT_LIT)
TP[ NO_TERMINALES['Expr'] ][ TERMINALES[TokenType.INT_LIT] ] = 11

# Regla 12: Expr ::= STRING_LIT             (si TA es STRING_LIT)
TP[ NO_TERMINALES['Expr'] ][ TERMINALES[TokenType.STRING_LIT] ] = 12

# Regla 13: Toggle ::= BOOL_ON LPAREN ID RPAREN  (si TA es BOOL_ON)
TP[ NO_TERMINALES['Toggle'] ][ TERMINALES[TokenType.BOOL_ON] ]  = 13

# Regla 14: Toggle ::= BOOL_OFF LPAREN ID RPAREN (si TA es BOOL_OFF)
TP[ NO_TERMINALES['Toggle'] ][ TERMINALES[TokenType.BOOL_OFF] ] = 14

# Regla 15: RepeatStmt ::= REPEATER ID ASSIGN Expr LBRACE StmtList RBRACE
#   (si TA es REPEATER)
TP[ NO_TERMINALES['RepeatStmt'] ][ TERMINALES[TokenType.REPEATER] ] = 15

# Regla 16: ArgList ::= Expr MoreArgs   (si TA en Expr: ID, INT_LIT, STRING_LIT)
for first in (TokenType.ID, TokenType.INT_LIT, TokenType.STRING_LIT):
    TP[ NO_TERMINALES['ArgList'] ][ TERMINALES[first] ] = 16

# Regla 17: ArgList ::= ε   (si TA es RPAREN)
TP[ NO_TERMINALES['ArgList'] ][ TERMINALES[TokenType.RPAREN] ] = 17

# Regla 18: MoreArgs ::= COMMA Expr MoreArgs (si TA es COMMA)
TP[ NO_TERMINALES['MoreArgs'] ][ TERMINALES[TokenType.COMMA] ] = 18

# Regla 19: MoreArgs ::= ε   (si TA es RPAREN)
TP[ NO_TERMINALES['MoreArgs'] ][ TERMINALES[TokenType.RPAREN] ] = 19

# Clase TokenStream para recorrer la lista de tokens

class TokenStream:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]  # EOF o token ficticio

    def next(self):
        if self.pos < len(self.tokens):
            t = self.tokens[self.pos]
            self.pos += 1
            return t
        return self.tokens[-1]

# Recuperación de errores

def recover_on_error(ts: TokenStream):
    """
    Avanza en el TokenStream hasta encontrar:
      - un ';' (TokenType.SEMICOLON)
      - un '}' (TokenType.RBRACE)
      - o EOF.
    Luego regresa para reintentar la derivación.
    """
    print("  [Re-sincronizando: buscando ';' o '}' o EOF...]")
    while True:
        tok = ts.next()
        if tok.type in (TokenType.SEMICOLON, TokenType.RBRACE, TokenType.EOF):
            print(f"  [Re-sincronizado en token {tok.type.name}]")
            return

# Driver principal de parsing

def parse_tokens(tokens):
    """
    Recibe la lista completa de tokens (etapa léxica ya terminada),
    y realiza el análisis sintáctico LL(1) con recuperación de errores.
    Devuelve una lista de mensajes de error (vacía si no hubo).
    """
    ts = TokenStream(tokens)
    errores = []

    # Inicializo TA (token actual) sin consumirlo aún
    TA = ts.peek()

    # Creo la pila de parsing y meto el símbolo inicial 'S'
    pila = Stack()
    pila.push(NO_TERMINALES['S'])

    # Mientras la pila no esté vacía:
    while not pila.is_empty():
        EAP = pila.pop()

        # --- CASO A: EAP es un terminal:
        if EAP >= OFFSET_T:
            terminal_index = EAP - OFFSET_T

            # Buscamos qué TokenType corresponde a ese índice
            expected_tok = None
            for tokype, idx in TERMINALES.items():
                if idx == terminal_index:
                    expected_tok = tokype
                    break

            if expected_tok is None:
                errores.append(f"[INTERNAL ERROR] Símbolo terminal desconocido: código={EAP}")
                return errores

            # Comparamos TA.type con expected_tok
            if TA.type == expected_tok:
                # Hizo match. Consumimos el token y seguimos
                TA = ts.next()
            else:
                errores.append(
                    f"Error sintáctico: esperaba '{expected_tok.name}' pero vino '{TA.type.name}' "
                    f"(lexema='{TA.lexeme}') en línea {TA.line}"
                )
                # Recuperación de error
                recover_on_error(ts)
                TA = ts.peek()
            continue

        # --- CASO B: EAP es un no terminal (0..NUM_NT-1)
        fila = EAP
        col = TERMINALES.get(TA.type, None)
        if col is None:
            # TA.type no está en TERMINALES → token inválido aquí
            errores.append(
                f"Error sintáctico: token inesperado '{TA.type.name}' (lexema='{TA.lexeme}') en línea {TA.line}"
            )
            recover_on_error(ts)
            TA = ts.peek()
            continue

        regla = TP[fila][col]
        if regla < 0:
            # No existe producción en la celda PREDICT(fila, col)
            nt_name = None
            for name, idx in NO_TERMINALES.items():
                if idx == fila:
                    nt_name = name
                    break
            errores.append(
                f"Error sintáctico en no terminal '{nt_name}': entrada '{TA.type.name}' "
                f"(lexema='{TA.lexeme}') no está en PREDICT"
            )
            recover_on_error(ts)
            TA = ts.peek()
            continue

        # Hay una regla válida: la metemos en la pila
        derecho = TLD[regla]
        if not (len(derecho) == 1 and derecho[0] == EPSILON):
            # Si no es epsilon, empujamos cada símbolo de derecha a izquierda
            for simbolo in reversed(derecho):
                pila.push(simbolo)
        # **Nota**: no consumimos TA aquí; solo avanzamos cuando hacemos match de un terminal.

    # Al salir, la pila ya está vacía. Debemos verificar que TA sea EOF.
    if TA.type != TokenType.EOF:
        errores.append(
            f"Error sintáctico: entrada no consumida al terminar el parser. "
            f"Token sobrante: '{TA.type.name}' (lexema='{TA.lexeme}') en línea {TA.line}"
        )
    else:
        # Si no hubo ningún error → agregamos indicador de “sin errores”
        errores.append("SIN_ERRORES")

    return errores

# Implementación de la pila

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
