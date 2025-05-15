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
            raise IOError("No se pudo cargar el primer buffer")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

def FinalizarScanner():
    """Cierra el archivo y libera recursos."""
    global _archivo
    if _archivo:
        _archivo.close()
        _archivo = None

def _peek():
    """Mira el siguiente carácter sin consumirlo."""
    if _peek_buffer:
        return _peek_buffer[0]
    
    c = DemeElSiguienteCaracter()
    _peek_buffer.append(c)
    return c

def _consume():
    """Consume un carácter (lo saca del buffer si existe)."""
    if _peek_buffer:
        return _peek_buffer.pop(0)
    else:
        return DemeElSiguienteCaracter()

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
    return 'a' <= c <= 'z' or 'A' <= c <= 'Z' or c == '_'

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
            lexema += _consume()
        else:
            break
    
    col_fin = _columna_actual - 1
    
    # Verificar si es una palabra clave
    tipo = _keywords.get(lexema.lower(), TokenType.ID)
    
    return Token(tipo, lexema, line=_linea_actual, col_start=col_inicio, col_end=col_fin)

def _procesar_numero():
    """Procesa un literal numérico (entero o flotante)."""
    col_inicio = _columna_actual
    lexema = ""
    
    # Verificar si es hexadecimal
    if _peek() == '0' and (_peek_buffer[1] if len(_peek_buffer) > 1 else DemeElSiguienteCaracter()) in 'xX':
        lexema += _consume()  # Consumir '0'
        lexema += _consume()  # Consumir 'x' o 'X'
        
        # Leer dígitos hexadecimales
        tiene_digitos = False
        while True:
            c = _peek()
            if ('0' <= c <= '9') or ('a' <= c <= 'f') or ('A' <= c <= 'F'):
                lexema += _consume()
                tiene_digitos = True
            else:
                break
        
        if not tiene_digitos:
            return Token(TokenType.ERROR, lexema, line=_linea_actual, col_start=col_inicio, 
                        col_end=_columna_actual-1, error_code=-1)
        
        valor = int(lexema, 16)
        return Token(TokenType.INT_LIT, lexema, valor, _linea_actual, col_inicio, _columna_actual-1)
    
    # Verificar si es octal
    if _peek() == '0' and (_peek_buffer[1] if len(_peek_buffer) > 1 else DemeElSiguienteCaracter()) != '.':
        lexema += _consume()  # Consumir '0'
        
        # Leer dígitos octales
        tiene_digitos = False
        while True:
            c = _peek()
            if '0' <= c <= '7':
                lexema += _consume()
                tiene_digitos = True
            else:
                break
        
        valor = int(lexema, 8) if tiene_digitos else 0
        return Token(TokenType.INT_LIT, lexema, valor, _linea_actual, col_inicio, _columna_actual-1)
    
    # Numero decimal (entero o flotante)
    es_flotante = False
    
    # Leer la parte entera
    while True:
        c = _peek()
        if _es_digito(c):
            lexema += _consume()
        else:
            break
    
    # Verificar si hay punto decimal
    if _peek() == '.':
        es_flotante = True
        lexema += _consume()
        
        # Leer la parte decimal
        while True:
            c = _peek()
            if _es_digito(c):
                lexema += _consume()
            else:
                break
    
    col_fin = _columna_actual - 1
    
    if es_flotante:
        valor = float(lexema)
        return Token(TokenType.FLOAT_LIT, lexema, valor, _linea_actual, col_inicio, col_fin)
    else:
        valor = int(lexema)
        return Token(TokenType.INT_LIT, lexema, valor, _linea_actual, col_inicio, col_fin)

def _procesar_caracter():
    """Procesa un literal de carácter."""
    col_inicio = _columna_actual
    lexema = "'"
    
    # Consumir la comilla de apertura
    _consume()
    
    # Leer el contenido del carácter
    c = _consume()
    if c == 'EOF':
        return Token(TokenType.ERROR, lexema, line=_linea_actual, col_start=col_inicio, 
                    col_end=_columna_actual-1, error_code=-2)
    
    lexema += c
    
    # Si es un escape
    if c == '\\':
        c = _consume()
        if c == 'EOF':
            return Token(TokenType.ERROR, lexema, line=_linea_actual, col_start=col_inicio, 
                        col_end=_columna_actual-1, error_code=-2)
        lexema += c
    
    # Consumir la comilla de cierre
    c = _consume()
    if c != "'":
        return Token(TokenType.ERROR, lexema, line=_linea_actual, col_start=col_inicio, 
                    col_end=_columna_actual-1, error_code=-3)
    
    lexema += c
    
    # Procesar el valor
    valor = lexema[1] if len(lexema) == 3 else lexema[1:3]
    
    return Token(TokenType.CHAR_LIT, lexema, valor, _linea_actual, col_inicio, _columna_actual-1)

def _procesar_string():
    """Procesa un literal de cadena."""
    col_inicio = _columna_actual
    lexema = '"'
    
    # Consumir la comilla de apertura
    _consume()
    
    # Leer el contenido de la cadena
    while True:
        c = _consume()
        if c == 'EOF':
            return Token(TokenType.ERROR, lexema, line=_linea_actual, col_start=col_inicio, 
                        col_end=_columna_actual-1, error_code=-4)
        
        lexema += c
        
        if c == '"':
            break
        
        # Si es un escape
        if c == '\\':
            c = _consume()
            if c == 'EOF':
                return Token(TokenType.ERROR, lexema, line=_linea_actual, col_start=col_inicio, 
                            col_end=_columna_actual-1, error_code=-4)
            lexema += c
    
    # Procesar el valor (quitar las comillas)
    valor = lexema[1:-1]
    
    return Token(TokenType.STRING_LIT, lexema, valor, _linea_actual, col_inicio, _columna_actual-1)

def _procesar_comentario():
    """Procesa un comentario."""
    col_inicio = _columna_actual
    lexema = ""
    
    # Consumir el primer '$'
    lexema += _consume()
    
    # Ver el siguiente carácter
    c = _peek()
    
    if c == '$':  # Comentario de línea
        lexema += _consume()
        
        # Leer hasta el final de la línea
        while True:
            c = _peek()
            if c == '\n' or c == 'EOF':
                break
            lexema += _consume()
            
    elif c == '*':  # Comentario de bloque
        lexema += _consume()
        
        # Leer hasta encontrar "*$"
        while True:
            c = _consume()
            if c == 'EOF':
                return Token(TokenType.ERROR, lexema, line=_linea_actual, col_start=col_inicio, 
                            col_end=_columna_actual-1, error_code=-5)
            
            lexema += c
            
            if c == '*' and _peek() == '$':
                lexema += _consume()  # Consumir el '$'
                break
    
    else:  # No es un comentario válido
        return Token(TokenType.ERROR, lexema, line=_linea_actual, col_start=col_inicio, 
                    col_end=_columna_actual-1, error_code=-6)
    
    return Token(TokenType.COMMENT, lexema, line=_linea_actual, col_start=col_inicio, col_end=_columna_actual-1)

def DemeToken():
    """Analiza y devuelve el siguiente token del archivo de entrada."""
    while True:
        c = _peek()
        
        # Fin de archivo
        if c == 'EOF':
            return Token(TokenType.EOF, "EOF", line=_linea_actual, col_start=_columna_actual, col_end=_columna_actual)
        
        # Ignorar espacios en blanco
        if _es_espaciador(c):
            _consume()
            continue
        
        # Identificadores o palabras clave
        if _es_letra(c):
            return _procesar_identificador_o_palabra_clave()
        
        # Números
        if _es_digito(c):
            return _procesar_numero()
        
        # Caracteres especiales
        if c == '(':
            _consume()
            return Token(TokenType.LPAREN, "(", line=_linea_actual, col_start=_columna_actual-1, col_end=_columna_actual-1)
        
        if c == ')':
            _consume()
            return Token(TokenType.RPAREN, ")", line=_linea_actual, col_start=_columna_actual-1, col_end=_columna_actual-1)
        
        if c == '{':
            _consume()
            # Verificar si es inicio de conjunto o registro
            if _peek() == ':':
                return Token(TokenType.LBRACE, "{:", line=_linea_actual, col_start=_columna_actual-1, col_end=_columna_actual)
            elif _peek() == '/':
                return Token(TokenType.LBRACE, "{/", line=_linea_actual, col_start=_columna_actual-1, col_end=_columna_actual)
            else:
                return Token(TokenType.LBRACE, "{", line=_linea_actual, col_start=_columna_actual-1, col_end=_columna_actual-1)
        
        if c == '}':
            _consume()
            return Token(TokenType.RBRACE, "}", line=_linea_actual, col_start=_columna_actual-1, col_end=_columna_actual-1)
        
        if c == '[':
            _consume()
            return Token(TokenType.LBRACKET, "[", line=_linea_actual, col_start=_columna_actual-1, col_end=_columna_actual-1)
        
        if c == ']':
            _consume()
            return Token(TokenType.RBRACKET, "]", line=_linea_actual, col_start=_columna_actual-1, col_end=_columna_actual-1)
        
        if c == ';':
            _consume()
            return Token(TokenType.SEMICOLON, ";", line=_linea_actual, col_start=_columna_actual-1, col_end=_columna_actual-1)
        
        if c == ':':
            _consume()
            if _peek() == '+':
                _consume()
                return Token(TokenType.FLOAT_OP, ":+", line=_linea_actual, col_start=_columna_actual-2, col_end=_columna_actual-1)
            elif _peek() == '-':
                _consume()
                return Token(TokenType.FLOAT_OP, ":-", line=_linea_actual, col_start=_columna_actual-2, col_end=_columna_actual-1)
            elif _peek() == '*':
                _consume()
                return Token(TokenType.FLOAT_OP, ":*", line=_linea_actual, col_start=_columna_actual-2, col_end=_columna_actual-1)
            elif _peek() == '/':
                if len(_peek_buffer) > 1 and _peek_buffer[1] == '/':
                    _consume()  # Consumir '/'
                    _consume()  # Consumir '/'
                    return Token(TokenType.FLOAT_OP, "://", line=_linea_actual, col_start=_columna_actual-3, col_end=_columna_actual-1)
            elif _peek() == '%':
                _consume()
                return Token(TokenType.FLOAT_OP, ":%", line=_linea_actual, col_start=_columna_actual-2, col_end=_columna_actual-1)
            elif _peek() == ':':
                _consume()
                return Token(TokenType.COLON, "::", line=_linea_actual, col_start=_columna_actual-2, col_end=_columna_actual-1)
            elif _peek() == '}':
                _consume()
                return Token(TokenType.COLON, ":}", line=_linea_actual, col_start=_columna_actual-2, col_end=_columna_actual-1)
            else:
                return Token(TokenType.COLON, ":", line=_linea_actual, col_start=_columna_actual-1, col_end=_columna_actual-1)
        
        if c == '.':
            _consume()
            return Token(TokenType.DOT, ".", line=_linea_actual, col_start=_columna_actual-1, col_end=_columna_actual-1)
        
        if c == ',':
            _consume()
            return Token(TokenType.COMMA, ",", line=_linea_actual, col_start=_columna_actual-1, col_end=_columna_actual-1)
        
        if c == '@':
            _consume()
            return Token(TokenType.AT, "@", line=_linea_actual, col_start=_columna_actual-1, col_end=_columna_actual-1)
        
        if c == '=':
            _consume()
            return Token(TokenType.ASSIGN, "=", line=_linea_actual, col_start=_columna_actual-1, col_end=_columna_actual-1)
        
        if c == '+':
            _consume()
            if _peek() == '=':
                _consume()
                return Token(TokenType.ASSIGN, "+=", line=_linea_actual, col_start=_columna_actual-2, col_end=_columna_actual-1)
            else:
                return Token(TokenType.PLUS, "+", line=_linea_actual, col_start=_columna_actual-1, col_end=_columna_actual-1)
        
        if c == '-':
            _consume()
            if _peek() == '=':
                _consume()
                return Token(TokenType.ASSIGN, "-=", line=_linea_actual, col_start=_columna_actual-2, col_end=_columna_actual-1)
            else:
                return Token(TokenType.MINUS, "-", line=_linea_actual, col_start=_columna_actual-1, col_end=_columna_actual-1)
        
        if c == '*':
            _consume()
            if _peek() == '=':
                _consume()
                return Token(TokenType.ASSIGN, "*=", line=_linea_actual, col_start=_columna_actual-2, col_end=_columna_actual-1)
            else:
                return Token(TokenType.MULTIPLY, "*", line=_linea_actual, col_start=_columna_actual-1, col_end=_columna_actual-1)
        
        if c == '/':
            _consume()
            if _peek() == '/':
                _consume()
                if _peek() == '=':
                    _consume()
                    return Token(TokenType.ASSIGN, "//=", line=_linea_actual, col_start=_columna_actual-3, col_end=_columna_actual-1)
                else:
                    return Token(TokenType.DIVIDE, "//", line=_linea_actual, col_start=_columna_actual-2, col_end=_columna_actual-1)
            elif _peek() == '}':
                _consume()
                return Token(TokenType.RBRACE, "/}", line=_linea_actual, col_start=_columna_actual-2, col_end=_columna_actual-1)
            else:
                return Token(TokenType.ERROR, "/", line=_linea_actual, col_start=_columna_actual-1, 
                            col_end=_columna_actual-1, error_code=-7)
        
        if c == '%':
            _consume()
            if _peek() == '=':
                _consume()
                return Token(TokenType.ASSIGN, "%=", line=_linea_actual, col_start=_columna_actual-2, col_end=_columna_actual-1)
            else:
                return Token(TokenType.MODULO, "%", line=_linea_actual, col_start=_columna_actual-1, col_end=_columna_actual-1)
        
        if c == '<':
            _consume()
            if _peek() == '=':
                _consume()
                return Token(TokenType.LE, "<=", line=_linea_actual, col_start=_columna_actual-2, col_end=_columna_actual-1)
            else:
                return Token(TokenType.LT, "<", line=_linea_actual, col_start=_columna_actual-1, col_end=_columna_actual-1)
        
        if c == '>':
            _consume()
            if _peek() == '=':
                _consume()
                return Token(TokenType.GE, ">=", line=_linea_actual, col_start=_columna_actual-2, col_end=_columna_actual-1)
            elif _peek() == '>':
                _consume()
                return Token(TokenType.COLON, ">>", line=_linea_actual, col_start=_columna_actual-2, col_end=_columna_actual-1)
            else:
                return Token(TokenType.GT, ">", line=_linea_actual, col_start=_columna_actual-1, col_end=_columna_actual-1)
        
        # Literales de carácter y cadena
        if c == "'":
            return _procesar_caracter()
        
        if c == '"':
            return _procesar_string()
        
        # Comentarios
        if c == '$':
            return _procesar_comentario()
        
        # Carácter desconocido (error)
        _consume()
        return Token(TokenType.ERROR, c, line=_linea_actual, col_start=_columna_actual-1, 
                    col_end=_columna_actual-1, error_code=-8)

def TomeToken():
    """Acepta el token actual."""
    global _token_actual
    _token_actual = None