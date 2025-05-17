from enum import Enum, auto
import re

# Definición de familias de tokens
class TokenType(Enum):
    # Palabras reservadas
    ANVIL = auto()
    BEDROCK = auto()
    BOOK = auto()
    CRAFTINGTABLE = auto()
    CHEST = auto()
    ENTITY = auto()
    GHAST = auto()
    INVENTORY = auto()
    OBSIDIAN = auto()
    POLLOCRUDO = auto()
    POLLOASADO = auto()
    RESOURCEPACK = auto()
    RECIPE = auto()
    RUNE = auto()
    REPEATER = auto()
    SPAWNPOINT = auto()
    STACK = auto()
    SPIDER = auto()
    SHELF = auto()
    TORCH = auto()
    WORLDNAME = auto()
    WORLDSAVE = auto()
    # Operadores
    ASSIGN = auto()       # =
    PLUS = auto()         # +
    MINUS = auto()        # -
    MULTIPLY = auto()     # *
    DIVIDE = auto()       # //
    FLOAT_OP = auto()     # :+, :-, :*, ://, :%
    MODULO = auto()       # %
    LT = auto()           # 
    GT = auto()           # >
    LE = auto()           # <=
    GE = auto()           # >=
    IS = auto()           # is
    ISNOT = auto()        # isNot
    EQ = auto()           # ==
    NE = auto()           # !=
    # Símbolos
    LPAREN = auto()       # (
    RPAREN = auto()       # )
    LBRACE = auto()       # {
    RBRACE = auto()       # }
    LBRACKET = auto()     # [
    RBRACKET = auto()     # ]
    SEMICOLON = auto()    # ;
    COLON = auto()        # :
    DOT = auto()          # .
    COMMA = auto()        # ,
    AT = auto()           # @
    # Literales
    ID = auto()           # Identificador
    INT_LIT = auto()      # Literal entero
    FLOAT_LIT = auto()    # Literal flotante
    CHAR_LIT = auto()     # Literal caracter
    STRING_LIT = auto()   # Literal string
    BOOL_ON = auto()      # On
    BOOL_OFF = auto()     # Off
    # Especiales
    EOF = auto()          # Fin de archivo
    ERROR = auto()        # Error léxico
    COMMENT = auto()      # Comentario

# Clase para representar un token
class Token:
    def __init__(self, type, lexeme, value=None, line=0, col_start=0, col_end=0, error_code=None):
        self.type = type          # Familia del token (TokenType)
        self.lexeme = lexeme      # Texto exacto encontrado
        self.value = value        # Valor traducido (para literales)
        self.line = line          # Número de línea
        self.col_start = col_start  # Columna de inicio
        self.col_end = col_end    # Columna final
        self.error_code = error_code  # Código de error si lo hay

    def __str__(self):
        if self.error_code:
            return f"ERROR[{self.error_code}]: '{self.lexeme}' en línea {self.line}, col {self.col_start}-{self.col_end}"
        elif self.value is not None:
            return f"{self.type.name}('{self.lexeme}', {self.value}) en línea {self.line}, col {self.col_start}-{self.col_end}"
        else:
            return f"{self.type.name}('{self.lexeme}') en línea {self.line}, col {self.col_start}-{self.col_end}"

# Variables globales para el scanner
_buffer = ""
_posicion = 0
_archivo = None
_linea_actual = 1
_columna_actual = 1
_token_actual = None
_peek_buffer = []  # Para almacenar caracteres "vistos" pero no consumidos

# Palabras reservadas del lenguaje
_keywords = {
    "anvil": TokenType.ANVIL,
    "bedrock": TokenType.BEDROCK,
    "book": TokenType.BOOK,
    "craftingtable": TokenType.CRAFTINGTABLE,
    "chest": TokenType.CHEST,
    "entity": TokenType.ENTITY,
    "ghast": TokenType.GHAST,
    "inventory": TokenType.INVENTORY,
    "obsidian": TokenType.OBSIDIAN,
    "pollocrudo": TokenType.POLLOCRUDO,
    "polloasado": TokenType.POLLOASADO,
    "resourcepack": TokenType.RESOURCEPACK,
    "recipe": TokenType.RECIPE,
    "rune": TokenType.RUNE,
    "repeater": TokenType.REPEATER,
    "spawnpoint": TokenType.SPAWNPOINT,
    "stack": TokenType.STACK,
    "spider": TokenType.SPIDER,
    "shelf": TokenType.SHELF,
    "torch": TokenType.TORCH,
    "worldname": TokenType.WORLDNAME,
    "worldsave": TokenType.WORLDSAVE,
    "on": TokenType.BOOL_ON,
    "off": TokenType.BOOL_OFF,
    "is": TokenType.IS,
    "isnot": TokenType.ISNOT
}

def InicializarScanner(nombre_archivo):
    """Abre el archivo y carga el primer buffer."""
    global _archivo, _buffer, _posicion, _linea_actual, _columna_actual, _token_actual
    try:
        _archivo = open(nombre_archivo, 'r', encoding='utf-8')
        _buffer = _archivo.read(4096)  # Leemos un buffer más grande
        _posicion = 0
        _linea_actual = 1
        _columna_actual = 1
        _token_actual = None
        if _buffer == '':
            raise IOError("Buffer inicial vacío")
    except Exception as e:
        print(f"InicializarScanner Error: {e}")
        exit(1)

def FinalizarScanner():
    """Cierra el archivo y libera recursos."""
    global _archivo
    if _archivo:
        _archivo.close()
        _archivo = None
    
def demecaracter():
    """Envoltura para DemeElSiguienteCaracter (lee sin registros de estado externos)."""
    return DemeElSiguienteCaracter()

def tomecaracter():
    """Envoltura para consumo de carácter con buffer."""
    if _peek_buffer:
        return _peek_buffer.pop(0)
    else:
        return DemeElSiguienteCaracter()

def _peek():
    """Mira el siguiente carácter sin consumirlo."""
    if _peek_buffer:
        return _peek_buffer[0]
    c = demecaracter()
    _peek_buffer.append(c)
    return c

def DemeElSiguienteCaracter():
    """Devuelve el siguiente carácter del archivo, usando un buffer."""
    global _buffer, _posicion, _archivo, _linea_actual, _columna_actual

    if _posicion >= len(_buffer):
        _buffer = _archivo.read(4096)
        _posicion = 0
        if _buffer == '':
            return 'EOF'

    caracter = _buffer[_posicion]
    _posicion += 1
    
    # Actualizar línea y columna
    if caracter == '\n':
        _linea_actual += 1
        _columna_actual = 1
    else:
        _columna_actual += 1
        
    return caracter

def _es_espaciador(c):
    """Verifica si un carácter es un espaciador."""
    return c in ' \t\n\r'

def _es_letra(c):
    """Verifica si un carácter es una letra."""
    return c.isalpha() or c == '_'

def _es_digito(c):
    """Verifica si un carácter es un dígito."""
    return '0' <= c <= '9'

def _procesar_identificador_o_palabra_clave():
    """Procesa un identificador o palabra clave."""
    col_inicio = _columna_actual
    lexema = ""
    
    while True:
        c = _peek()
        if _es_letra(c) or _es_digito(c):
            lexema += tomecaracter()
        else:
            break
    
    col_fin = _columna_actual - 1
    
    # Verificar si es una palabra clave
    tipo = _keywords.get(lexema.lower(), TokenType.ID)
    
    return Token(tipo, lexema, line=_linea_actual, col_start=col_inicio, col_end=col_fin)

def _procesar_numero():
    """Procesa números enteros, flotantes y notación científica."""
    col_inicio = _columna_actual
    lexema = ""
    tiene_punto = False
    tiene_exponente = False

    while True:
        c = _peek()

        if _es_digito(c):
            lexema += tomecaracter()

        elif c == '.':
            if tiene_punto:
                # Segundo punto decimal = error
                lexema += tomecaracter()
                return Token(TokenType.ERROR, lexema, line=_linea_actual,
                             col_start=col_inicio, col_end=_columna_actual-1, error_code=-7)
            tiene_punto = True
            lexema += tomecaracter()

        elif c in 'eE':
            if tiene_exponente:
                # Segundo exponente = error
                lexema += tomecaracter()
                return Token(TokenType.ERROR, lexema, line=_linea_actual,
                             col_start=col_inicio, col_end=_columna_actual-1, error_code=-9)
            tiene_exponente = True
            lexema += tomecaracter()

            # Puede venir signo + o -
            if _peek() in '+-':
                lexema += tomecaracter()

            # Debe venir al menos un dígito
            if not _es_digito(_peek()):
                return Token(TokenType.ERROR, lexema, line=_linea_actual,
                             col_start=col_inicio, col_end=_columna_actual-1, error_code=-10)

        else:
            break

    col_final = _columna_actual-1

    # Ahora determina tipo
    if tiene_punto or tiene_exponente:
        try:
            valor = float(lexema)
            return Token(TokenType.FLOAT_LIT, lexema, value=valor, line=_linea_actual,
                         col_start=col_inicio, col_end=col_final)
        except ValueError:
            return Token(TokenType.ERROR, lexema, line=_linea_actual,
                         col_start=col_inicio, col_end=col_final, error_code=-11)
    else:
        valor = int(lexema)
        return Token(TokenType.INT_LIT, lexema, value=valor, line=_linea_actual,
                     col_start=col_inicio, col_end=col_final)

def _procesar_caracter():
    """Procesa un literal de carácter."""
    col_inicio = _columna_actual
    lexema = "'"
    
    # Consumir la comilla de apertura
    tomecaracter()
    
    # Leer el contenido del carácter
    c = tomecaracter()
    if c == 'EOF':
        return Token(TokenType.ERROR, lexema, line=_linea_actual, col_start=col_inicio, 
                    col_end=_columna_actual-1, error_code=-2)
    
    lexema += c
    
    # Si es un escape
    if c == '\\':
        c = tomecaracter()
        if c == 'EOF':
            return Token(TokenType.ERROR, lexema, line=_linea_actual, col_start=col_inicio, 
                        col_end=_columna_actual-1, error_code=-2)
        lexema += c
    
    # Consumir la comilla de cierre
    c = tomecaracter()
    if c != "'":
        return Token(TokenType.ERROR, lexema, line=_linea_actual, col_start=col_inicio, 
                    col_end=_columna_actual-1, error_code=-3)
    
    lexema += c
    
    # Procesar el valor
    valor = lexema[1] if len(lexema) == 3 else lexema[1:3]
    
    return Token(TokenType.CHAR_LIT, lexema, valor, _linea_actual, col_inicio, _columna_actual-1)

def _procesar_string():
    """Procesa literales de cadena."""
    col_inicio = _columna_actual
    lexema = ""
    valor = ""

    lexema += tomecaracter()  # Consume '"'

    while True:
        c = _peek()

        if c == 'EOF':
            return Token(TokenType.ERROR, lexema, line=_linea_actual,
                         col_start=col_inicio, col_end=_columna_actual-1, error_code=-4)

        elif c == '\n':
            return Token(TokenType.ERROR, lexema, line=_linea_actual,
                         col_start=col_inicio, col_end=_columna_actual-1, error_code=-4)

        elif c == '\"':
            lexema += tomecaracter()
            break

        elif c == '\\':
            lexema += tomecaracter()  # Consume '\'
            esc = _peek()
            if esc in ['n', 't', '\"', '\\']:
                lexema += tomecaracter()
                if esc == 'n':
                    valor += '\n'
                elif esc == 't':
                    valor += '\t'
                elif esc == '\"':
                    valor += '\"'
                elif esc == '\\':
                    valor += '\\'
            else:
                # Escape inválido
                lexema += tomecaracter()
                return Token(TokenType.ERROR, lexema, line=_linea_actual,
                             col_start=col_inicio, col_end=_columna_actual-1, error_code=-12)

        else:
            lexema += tomecaracter()
            valor += c

    col_final = _columna_actual-1
    return Token(TokenType.STRING_LIT, lexema, value=valor, line=_linea_actual,
                 col_start=col_inicio, col_end=col_final)

def _procesar_comentario():
    """Procesa un comentario."""
    col_inicio = _columna_actual
    lexema = ""
    
    # Consumir el primer '$'
    lexema += '$'
    
    # Ver el siguiente carácter
    c = _peek()
    
    if c == '$':  # Comentario de línea
        lexema += tomecaracter()
        
        # Leer hasta el final de la línea
        while True:
            c = _peek()
            if c == '\n' or c == 'EOF':
                break
            lexema += tomecaracter()
            
    elif c == '*':  # Comentario de bloque
        lexema += tomecaracter()
        
        # Leer hasta encontrar "*$"
        while True:
            c = tomecaracter()
            if c == 'EOF':
                return Token(TokenType.ERROR, lexema, line=_linea_actual, col_start=col_inicio, 
                            col_end=_columna_actual-1, error_code=-5)
            
            lexema += c
            
            if c == '*' and _peek() == '$':
                lexema += tomecaracter()  # Consumir el '$'
                break
    
    else:  # No es un comentario válido
        return Token(TokenType.ERROR, lexema, line=_linea_actual, col_start=col_inicio, 
                    col_end=_columna_actual-1, error_code=-6)
    
    return Token(TokenType.COMMENT, lexema, line=_linea_actual, col_start=col_inicio, col_end=_columna_actual-1)

def DemeToken():
    """Devuelve el siguiente token, saltando sobre errores para recuperación."""
    global _token_actual
    while True:
        c = _peek()

        # Fin de archivo
        if c == 'EOF':
            start_line = _linea_actual
            start_col  = _columna_actual
            tomecaracter()
            return Token(TokenType.EOF, "EOF",
                         line=start_line,
                         col_start=start_col,
                         col_end=start_col)

        # Espaciadores
        if _es_espaciador(c):
            tomecaracter()
            continue

        # Letras: identificadores o palabra clave
        if _es_letra(c):
            # _procesar_identificador... ya usa col_inicio/fin
            _token_actual = _procesar_identificador_o_palabra_clave()
            return _token_actual

        # Dígitos: números
        if _es_digito(c):
            _token_actual = _procesar_numero()
            return _token_actual

        # División entera // o slash suelto
        if c == '/':
            start_line = _linea_actual
            start_col  = _columna_actual
            tomecaracter()      # consume primer '/'
            if _peek() == '/':
                tomecaracter()  # consume segundo '/'
                _token_actual = Token(TokenType.DIVIDE, "//",
                                       line=start_line,
                                       col_start=start_col,
                                       col_end=_columna_actual-1)
            else:
                _token_actual = Token(TokenType.ERROR, "/",
                                       line=start_line,
                                       col_start=start_col,
                                       col_end=start_col,
                                       error_code=-8)
            return _token_actual

        # Operadores y símbolos
        if c in "(){}[];.,@=:+-*%<>$\"'!":
            start_line = _linea_actual
            start_col  = _columna_actual
            ch = tomecaracter()

            # '=' o '=='
            if ch == "=":
                if _peek() == "=":
                    tomecaracter()
                    lex = "=="
                    end_col = _columna_actual-1
                    _token_actual = Token(TokenType.EQ, lex,
                                          line=start_line,
                                          col_start=start_col,
                                          col_end=end_col)
                else:
                    _token_actual = Token(TokenType.ASSIGN, "=",
                                          line=start_line,
                                          col_start=start_col,
                                          col_end=start_col)

            # '!=' o '!'
            elif ch == "!":
                if _peek() == "=":
                    tomecaracter()
                    lex = "!="
                    end_col = _columna_actual-1
                    _token_actual = Token(TokenType.NE, lex,
                                          line=start_line,
                                          col_start=start_col,
                                          col_end=end_col)
                else:
                    _token_actual = Token(TokenType.ERROR, "!",
                                          line=start_line,
                                          col_start=start_col,
                                          col_end=start_col,
                                          error_code=-8)

            # '<' or '<='
            elif ch == "<":
                if _peek() == "=":
                    tomecaracter()
                    lex = "<="
                    end_col = _columna_actual-1
                    _token_actual = Token(TokenType.LE, lex,
                                          line=start_line,
                                          col_start=start_col,
                                          col_end=end_col)
                else:
                    _token_actual = Token(TokenType.LT, "<",
                                          line=start_line,
                                          col_start=start_col,
                                          col_end=start_col)

            # '>' or '>='
            elif ch == ">":
                if _peek() == "=":
                    tomecaracter()
                    lex = ">="
                    end_col = _columna_actual-1
                    _token_actual = Token(TokenType.GE, lex,
                                          line=start_line,
                                          col_start=start_col,
                                          col_end=end_col)
                else:
                    _token_actual = Token(TokenType.GT, ">",
                                          line=start_line,
                                          col_start=start_col,
                                          col_end=start_col)

            # Float ops prefijados con ':'
            elif ch == ":":
                nxt = _peek()
                if nxt in ["+", "-", "*", "%"]:
                    lex = ch + tomecaracter()
                    end_col = _columna_actual-1
                    _token_actual = Token(TokenType.FLOAT_OP, lex,
                                          line=start_line,
                                          col_start=start_col,
                                          col_end=end_col)
                elif nxt == "/":
                    tomecaracter()
                    if _peek() == "/":
                        tomecaracter()
                        lex = "://"
                        end_col = _columna_actual-1
                        _token_actual = Token(TokenType.FLOAT_OP, lex,
                                              line=start_line,
                                              col_start=start_col,
                                              col_end=end_col)
                    else:
                        _token_actual = Token(TokenType.ERROR, ":/",
                                              line=start_line,
                                              col_start=start_col,
                                              col_end=_columna_actual-1,
                                              error_code=-8)
                else:
                    _token_actual = Token(TokenType.COLON, ":",
                                          line=start_line,
                                          col_start=start_col,
                                          col_end=start_col)

            # Comentarios, cadenas y caracteres
            elif ch == "$":
                _token_actual = _procesar_comentario()
            elif ch == "\"":
                _token_actual = _procesar_string()
            elif ch == "'":
                _token_actual = _procesar_caracter()

            # Resto de símbolos sencillos
            else:
                token_map = {
                    "(": TokenType.LPAREN,    ")": TokenType.RPAREN,
                    "{": TokenType.LBRACE,    "}": TokenType.RBRACE,
                    "[": TokenType.LBRACKET,  "]": TokenType.RBRACKET,
                    ";": TokenType.SEMICOLON, ",": TokenType.COMMA,
                    ".": TokenType.DOT,       "+": TokenType.PLUS,
                    "-": TokenType.MINUS,     "*": TokenType.MULTIPLY,
                    "%": TokenType.MODULO,    "@": TokenType.AT
                }
                tok_type = token_map.get(ch)
                if tok_type:
                    _token_actual = Token(tok_type, ch,
                                          line=start_line,
                                          col_start=start_col,
                                          col_end=start_col)
                else:
                    _token_actual = Token(TokenType.ERROR, ch,
                                          line=start_line,
                                          col_start=start_col,
                                          col_end=start_col,
                                          error_code=-8)

            return _token_actual

        # Carácter desconocido -> error
        start_line = _linea_actual
        start_col  = _columna_actual
        tomecaracter()
        _token_actual = Token(TokenType.ERROR, c,
                              line=start_line,
                              col_start=start_col,
                              col_end=start_col,
                              error_code=-8)
        return _token_actual


def TomeToken():
    """Acepta el token actual."""
    global _token_actual
    _token_actual = None