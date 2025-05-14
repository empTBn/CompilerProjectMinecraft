# lexico.py
# Versión en Python del analizador léxico básico

BUFFER_SIZE = 128
_buffer = ""
_posicion = 0
_archivo = None

def InicializarScanner(nombre_archivo):
    """Abre el archivo y carga el primer buffer."""
    global _archivo, _buffer, _posicion
    try:
        _archivo = open(nombre_archivo, 'r', encoding='utf-8')
        _buffer = _archivo.read(BUFFER_SIZE)
        _posicion = 0
        if _buffer == '':
            raise IOError("No se pudo cargar el primer buffer")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

def DemeElSiguienteCaracter():
    """Devuelve el siguiente carácter del archivo, usando un buffer."""
    global _buffer, _posicion, _archivo

    if _posicion >= len(_buffer):
        _buffer = _archivo.read(BUFFER_SIZE)
        _posicion = 0
        if _buffer == '':
            return 'EOF'

    caracter = _buffer[_posicion]
    _posicion += 1
    return caracter

def FinalizarScanner():
    """Cierra el archivo y libera recursos."""
    global _archivo
    if _archivo:
        _archivo.close()
        _archivo = None
