# parser.py

from scanner import TokenType
from rutinas_semanticas import (
    declare_variable,
    check_variable_exists,
    check_assignment_types,
    push_literal_type,
    push_variable_type,
    mark_variable_initialized,
    dump_symbol_table
)

# ------------------------------------------------------------
# 1) Mapeo de terminales a índices 
# ------------------------------------------------------------
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
    TokenType.IS:           24,
    TokenType.ISNOT:        25,
    TokenType.ID:           26,
    TokenType.INT_LIT:      27,
    TokenType.FLOAT_LIT:    28,
    TokenType.CHAR_LIT:     29,
    TokenType.STRING_LIT:   30,
    TokenType.LPAREN:       31,
    TokenType.RPAREN:       32,
    TokenType.LBRACE:       33,
    TokenType.RBRACE:       34,
    TokenType.LBRACKET:     35,
    TokenType.RBRACKET:     36,
    TokenType.SEMICOLON:    37,
    TokenType.COLON:        38,
    TokenType.DOT:          39,
    TokenType.COMMA:        40,
    TokenType.AT:           41,
    TokenType.PLUS:         42,
    TokenType.MINUS:        43,
    TokenType.MULTIPLY:     44,
    TokenType.DIVIDE:       45,   # '//'
    TokenType.FLOAT_OP:     46,   # ':+', ':-', ':*', '://', ':%'
    TokenType.MODULO:       47,
    TokenType.LT:           48,
    TokenType.GT:           49,
    TokenType.LE:           50,
    TokenType.GE:           51,
    TokenType.EQ:           52,
    TokenType.NE:           53,
    TokenType.COMMENT:      54,
    TokenType.EOF:          55,
    TokenType.ERROR:        56,   # (no se usa en el parser)
}

NUM_T = len(TERMINALES)

# ------------------------------------------------------------
# 2) No terminales 
# ------------------------------------------------------------
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

# Valor de “epsilon” (cuando la producción no genera nada)
EPSILON = -2

OFFSET_T = NUM_NT

# ------------------------------------------------------------
# 3) Tabla de Lados Derechos
# ------------------------------------------------------------
TLD = [
    # 0: S ::= WorldDecl
    [ NO_TERMINALES['WorldDecl'] ],

    # 1: WorldDecl ::= WORLDNAME ID COLON LBRACE StmtList RBRACE
    [
      OFFSET_T + TERMINALES[TokenType.WORLDNAME],
      OFFSET_T + TERMINALES[TokenType.ID],
      OFFSET_T + TERMINALES[TokenType.COLON],
      OFFSET_T + TERMINALES[TokenType.LBRACE],
      NO_TERMINALES['StmtList'],
      OFFSET_T + TERMINALES[TokenType.RBRACE]
    ],

    # 2: StmtList ::= Stmt StmtList
    [ NO_TERMINALES['Stmt'], NO_TERMINALES['StmtList'] ],

    # 3: StmtList ::= ε
    [ EPSILON ],

    # 4: Stmt ::= EntityCall SEMICOLON
    [ NO_TERMINALES['EntityCall'], OFFSET_T + TERMINALES[TokenType.SEMICOLON] ],

    # 5: Stmt ::= Assignment SEMICOLON
    [ NO_TERMINALES['Assignment'], OFFSET_T + TERMINALES[TokenType.SEMICOLON] ],

    # 6: Stmt ::= Toggle SEMICOLON
    [ NO_TERMINALES['Toggle'], OFFSET_T + TERMINALES[TokenType.SEMICOLON] ],

    # 7: Stmt ::= RepeatStmt
    [ NO_TERMINALES['RepeatStmt'] ],

    # 8: EntityCall ::= KEYWORD LPAREN ArgList RPAREN
    [
      OFFSET_T + TERMINALES[TokenType.ANVIL],        # (reemplazado dinámicamente por TP)
      OFFSET_T + TERMINALES[TokenType.LPAREN],
      NO_TERMINALES['ArgList'],
      OFFSET_T + TERMINALES[TokenType.RPAREN]
    ],

    # 9: Assignment ::= ID ASSIGN Expr
    [
      OFFSET_T + TERMINALES[TokenType.ID],
      OFFSET_T + TERMINALES[TokenType.ASSIGN],
      NO_TERMINALES['Expr']
    ],

    # 10: Expr ::= ID
    [ OFFSET_T + TERMINALES[TokenType.ID] ],

    # 11: Expr ::= INT_LIT
    [ OFFSET_T + TERMINALES[TokenType.INT_LIT] ],

    # 12: Expr ::= STRING_LIT
    [ OFFSET_T + TERMINALES[TokenType.STRING_LIT] ],

    # 13: Toggle ::= BOOL_ON LPAREN ID RPAREN
    [
      OFFSET_T + TERMINALES[TokenType.BOOL_ON],
      OFFSET_T + TERMINALES[TokenType.LPAREN],
      OFFSET_T + TERMINALES[TokenType.ID],
      OFFSET_T + TERMINALES[TokenType.RPAREN]
    ],

    # 14: Toggle ::= BOOL_OFF LPAREN ID RPAREN
    [
      OFFSET_T + TERMINALES[TokenType.BOOL_OFF],
      OFFSET_T + TERMINALES[TokenType.LPAREN],
      OFFSET_T + TERMINALES[TokenType.ID],
      OFFSET_T + TERMINALES[TokenType.RPAREN]
    ],

    # 15: RepeatStmt ::= REPEATER ID ASSIGN Expr LBRACE StmtList RBRACE
    [
      OFFSET_T + TERMINALES[TokenType.REPEATER],
      OFFSET_T + TERMINALES[TokenType.ID],
      OFFSET_T + TERMINALES[TokenType.ASSIGN],
      NO_TERMINALES['Expr'],
      OFFSET_T + TERMINALES[TokenType.LBRACE],
      NO_TERMINALES['StmtList'],
      OFFSET_T + TERMINALES[TokenType.RBRACE]
    ],

    # 16: ArgList ::= Expr MoreArgs
    [ NO_TERMINALES['Expr'], NO_TERMINALES['MoreArgs'] ],

    # 17: ArgList ::= ε
    [ EPSILON ],

    # 18: MoreArgs ::= COMMA Expr MoreArgs
    [
      OFFSET_T + TERMINALES[TokenType.COMMA],
      NO_TERMINALES['Expr'],
      NO_TERMINALES['MoreArgs']
    ],

    # 19: MoreArgs ::= ε
    [ EPSILON ],
]

# ------------------------------------------------------------
# 4) Construcción de la Tabla de Parsing (TP)
# ------------------------------------------------------------
TP = [[-1] * NUM_T for _ in range(NUM_NT)]

# Regla 0: S ::= WorldDecl  (si TA es WORLDNAME)
TP[ NO_TERMINALES['S']           ][ TERMINALES[TokenType.WORLDNAME] ] = 0

# Regla 1: WorldDecl ::= WORLDNAME ID COLON LBRACE StmtList RBRACE
TP[ NO_TERMINALES['WorldDecl']   ][ TERMINALES[TokenType.WORLDNAME] ] = 1

# Regla 2: StmtList ::= Stmt StmtList     (si TA en {Entity-keywords, ID, BOOL_ON, BOOL_OFF, REPEATER})
for first_token in (
    TokenType.ANVIL, TokenType.BEDROCK, TokenType.BOOK, TokenType.CRAFTINGTABLE,
    TokenType.CHEST, TokenType.ENTITY, TokenType.GHAST, TokenType.INVENTORY,
    TokenType.OBSIDIAN, TokenType.POLLOCRUDO, TokenType.POLLOASADO, TokenType.RESOURCEPACK,
    TokenType.RECIPE, TokenType.RUNE, TokenType.REPEATER, TokenType.SPAWNPOINT,
    TokenType.STACK, TokenType.SPIDER, TokenType.SHELF, TokenType.TORCH,
    TokenType.WORLDSAVE,
    TokenType.ID,
    TokenType.BOOL_ON, TokenType.BOOL_OFF
):
    TP[ NO_TERMINALES['StmtList'] ][ TERMINALES[first_token] ] = 2

# Regla 3: StmtList ::= ε   (si TA es RBRACE o EOF)
for t in (TokenType.RBRACE, TokenType.EOF):
    TP[ NO_TERMINALES['StmtList'] ][ TERMINALES[t] ] = 3

# Regla 4: Stmt ::= EntityCall SEMICOLON    (si TA es alguna de las keywords de entidad)
for kw in (
    TokenType.ANVIL, TokenType.BEDROCK, TokenType.BOOK, TokenType.CRAFTINGTABLE,
    TokenType.CHEST, TokenType.ENTITY, TokenType.GHAST, TokenType.INVENTORY,
    TokenType.OBSIDIAN, TokenType.POLLOCRUDO, TokenType.POLLOASADO, TokenType.RESOURCEPACK,
    TokenType.RECIPE, TokenType.RUNE, TokenType.SPAWNPOINT, TokenType.STACK,
    TokenType.SPIDER, TokenType.SHELF, TokenType.TORCH, TokenType.WORLDSAVE
):
    TP[ NO_TERMINALES['Stmt'] ][ TERMINALES[kw] ] = 4

# Regla 5: Stmt ::= Assignment SEMICOLON      (si TA es ID)
TP[ NO_TERMINALES['Stmt'] ][ TERMINALES[TokenType.ID] ] = 5

# Regla 6: Stmt ::= Toggle SEMICOLON          (si TA es BOOL_ON o BOOL_OFF)
TP[ NO_TERMINALES['Stmt'] ][ TERMINALES[TokenType.BOOL_ON] ]  = 6
TP[ NO_TERMINALES['Stmt'] ][ TERMINALES[TokenType.BOOL_OFF] ] = 6

# Regla 7: Stmt ::= RepeatStmt               (si TA es REPEATER)
TP[ NO_TERMINALES['Stmt'] ][ TERMINALES[TokenType.REPEATER] ] = 7

# Regla 8: EntityCall ::= KEYWORD LPAREN ArgList RPAREN 
for kw in (
    TokenType.ANVIL, TokenType.BEDROCK, TokenType.BOOK, TokenType.CRAFTINGTABLE,
    TokenType.CHEST, TokenType.ENTITY, TokenType.GHAST, TokenType.INVENTORY,
    TokenType.OBSIDIAN, TokenType.POLLOCRUDO, TokenType.POLLOASADO, TokenType.RESOURCEPACK,
    TokenType.RECIPE, TokenType.RUNE, TokenType.SPAWNPOINT, TokenType.STACK,
    TokenType.SPIDER, TokenType.SHELF, TokenType.TORCH, TokenType.WORLDSAVE
):
    TP[ NO_TERMINALES['EntityCall'] ][ TERMINALES[kw] ] = 8

# Regla 9: Assignment ::= ID ASSIGN Expr
TP[ NO_TERMINALES['Assignment'] ][ TERMINALES[TokenType.ID] ] = 9

# Regla 10: Expr ::= ID
TP[ NO_TERMINALES['Expr'] ][ TERMINALES[TokenType.ID] ] = 10

# Regla 11: Expr ::= INT_LIT
TP[ NO_TERMINALES['Expr'] ][ TERMINALES[TokenType.INT_LIT] ] = 11

# Regla 12: Expr ::= STRING_LIT
TP[ NO_TERMINALES['Expr'] ][ TERMINALES[TokenType.STRING_LIT] ] = 12

# Regla 13: Toggle ::= BOOL_ON LPAREN ID RPAREN
TP[ NO_TERMINALES['Toggle'] ][ TERMINALES[TokenType.BOOL_ON] ]  = 13

# Regla 14: Toggle ::= BOOL_OFF LPAREN ID RPAREN
TP[ NO_TERMINALES['Toggle'] ][ TERMINALES[TokenType.BOOL_OFF] ] = 14

# Regla 15: RepeatStmt ::= REPEATER ID ASSIGN Expr LBRACE StmtList RBRACE
TP[ NO_TERMINALES['RepeatStmt'] ][ TERMINALES[TokenType.REPEATER] ] = 15

# Regla 16: ArgList ::= Expr MoreArgs    (si TA en {ID, INT_LIT, STRING_LIT})
for f in (TokenType.ID, TokenType.INT_LIT, TokenType.STRING_LIT):
    TP[ NO_TERMINALES['ArgList'] ][ TERMINALES[f] ] = 16

# Regla 17: ArgList ::= ε    (si TA es RPAREN)
TP[ NO_TERMINALES['ArgList'] ][ TERMINALES[TokenType.RPAREN] ] = 17

# Regla 18: MoreArgs ::= COMMA Expr MoreArgs  (si TA es COMMA)
TP[ NO_TERMINALES['MoreArgs'] ][ TERMINALES[TokenType.COMMA] ] = 18

# Regla 19: MoreArgs ::= ε    (si TA es RPAREN)
TP[ NO_TERMINALES['MoreArgs'] ][ TERMINALES[TokenType.RPAREN] ] = 19

# ------------------------------------------------------------
# 5) Para recorrer la lista de tokens
# ------------------------------------------------------------
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

# ------------------------------------------------------------
# 6) Rutina de recuperación de errores 
# ------------------------------------------------------------
def recover_on_error(ts: TokenStream):
    print("  [Re-sincronizando: buscando ';' o '}' o EOF…]")
    while True:
        tok = ts.next()
        if tok.type in (TokenType.SEMICOLON, TokenType.RBRACE, TokenType.EOF):
            print(f"  [Re-sincronizado en token {tok.type.name}]")
            return

# ------------------------------------------------------------
# 7) Driver principal de parsing con llamadas semánticas
# ------------------------------------------------------------
def parse_tokens(tokens):
    ts = TokenStream(tokens)
    errores = []

    TA = ts.peek()                    # Token actual (sin consumir aún)
    pila = Stack()
    pila.push(NO_TERMINALES['S'])     # Empezamos con el símbolo inicial S

    # Variables auxiliares para chequeos semánticos en Assignments
    left_assign_token = None  # guardará el ID de la LHS cuando estemos reduciendo “Assignment”

    while not pila.is_empty():
        EAP = pila.pop()

        # CASO A: EAP es un terminal
        if EAP >= OFFSET_T:
            terminal_index = EAP - OFFSET_T

            # ¿Qué TokenType corresponde a ese índice?
            expected_tok = None
            for tokype, idx in TERMINALES.items():
                if idx == terminal_index:
                    expected_tok = tokype
                    break

            if expected_tok is None:
                errores.append(f"[INTERNAL] Terminal desconocido: código={EAP}")
                return errores

            # Hacemos match: si coincide, consumimos TA, si no → error + resincronizar
            if TA.type == expected_tok:
                # Antes de consumir, inyectamos ciertas acciones semánticas:
                #  1) Si estamos reduciendo “Assignment ::= ID ASSIGN Expr”:
                if left_assign_token is None and expected_tok == TokenType.ID:
                    # Podría ser el ID de la LHS de Assignment: lo guardamos
                    left_assign_token = TA

                #  2) Si es un literal dentro de Expr
                if expected_tok == TokenType.INT_LIT or expected_tok == TokenType.STRING_LIT:
                    push_literal_type(TA)

                #  3) Si es un ID dentro de Expr o Toggle o RepeatStmt
                if expected_tok == TokenType.ID:
                    # Chequeamos existencia y empujamos su tipo
                    check_variable_exists(TA.lexeme, TA.line)
                    push_variable_type(TA)

                #  4) Si acabamos de consumir “ASSIGN” en Assignment:
                if expected_tok == TokenType.ASSIGN and left_assign_token is not None:
                    # Llamamos a declare_variable(...) en el LHS (si no existe, lo creamos)
                    declare_variable(left_assign_token.lexeme, left_assign_token.line)

                TA = ts.next()
            else:
                errores.append(
                    f"Error sintáctico: esperaba '{expected_tok.name}' "
                    f"pero vino '{TA.type.name}' (lexema='{TA.lexeme}') en línea {TA.line}"
                )
                recover_on_error(ts)
                TA = ts.peek()
            continue

        # CASO B: EAP es un no terminal
        fila = EAP
        col = TERMINALES.get(TA.type, None)
        if col is None:
            errores.append(
                f"Error sintáctico: token inesperado '{TA.type.name}' (lexema='{TA.lexeme}') en línea {TA.line}"
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
                f"entrada '{TA.type.name}' (lexema='{TA.lexeme}') no está en PREDICT"
            )
            recover_on_error(ts)
            TA = ts.peek()
            continue

        derecho = TLD[regla]
        if not (len(derecho) == 1 and derecho[0] == EPSILON):
            for simbolo in reversed(derecho):
                pila.push(simbolo)

        # ------- AÑADIMOS LLAMADAS SEMÁNTICAS según la regla -------

        #  - Si la regla es  9: “Assignment ::= ID ASSIGN Expr”
        #    después de reducir todo Expr, debemos invocar check_assignment_types.
        if regla == 9:
            # Cuando la parte Expr ya se haya consumido por completo, TA habrá sido actualizado.
            # Podemos tomar el último literal o ID que se apiló en la pila de tipos para el RHS.
            # Para simplificar, asumimos que “right_token” está en TA-previo a la llamada:
            right_token = TA
            if left_assign_token is not None:
                check_assignment_types(left_assign_token, right_token)
            left_assign_token = None  # reseteamos

        #  - Si la regla es 13 o 14 (Toggle), el ID que consumimos dentro de Toggle ya fue chequeado
        #    vía check_variable_exists en el bloque “match terminal”.

        #  - Si la regla es 15 (RepeatStmt ::= REPEATER ID ASSIGN Expr LBRACE StmtList RBRACE):
        #    Para el ID en la posición 1, checamos existencia y tipo (int).
        if regla == 15:
            # El token ID fue chequeado en el “match terminal”; 
            # en ese momento, push_variable_type() lo colocó en la pila de tipos.
            # Aquí podríamos pop() y verificar que sea “int”:
            pass  # ya se maneja parcialmente en “match terminal”


    # Al salir del while, la pila quedó vacía. Debemos verificar que TA sea EOF.
    if TA.type != TokenType.EOF:
        errores.append(
            f"Error sintáctico: entrada no consumida al terminar el parser. "
            f"Token sobrante: '{TA.type.name}' (lexema='{TA.lexeme}') en línea {TA.line}"
        )
    else:
        errores.append("SIN_ERRORES")

    # Para propósitos de depuración, volcamos la tabla de símbolos
    print("\n--- Contenido de la Tabla de Símbolos al final del parseo: ---")
    dump_symbol_table()

    return errores

# ------------------------------------------------------------
# 8) Implementación de la pila (Stack)
# ------------------------------------------------------------
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
