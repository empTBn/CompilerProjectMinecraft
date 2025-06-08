class SymbolInfo:
    """
    Representa la información asociada a un identificador

    """
    def __init__(self, name: str, kind: str, tipe: str, initialized: bool = False):
        self.name = name
        self.kind = kind
        self.type = tipe
        self.initialized = initialized

class SymbolTable:
    """
    Tabla de símbolos simple 
    """
    def __init__(self):
        # Diccionario que mapea nombre (string) → SymbolInfo
        self._table = {}

    def exists(self, name: str) -> bool:
        """Devuelve True si el identificador ya existe."""
        return name in self._table

    def lookup(self, name: str) -> SymbolInfo:
        """Retorna el SymbolInfo de 'name', o None si no existe."""
        return self._table.get(name, None)

    def insert(self, name: str, kind: str, tipe: str) -> bool:
        """
        Inserta un nuevo símbolo. 
        Devuelve False si ya existía (error), True si se agregó correctamente.
        """
        if self.exists(name):
            return False
        self._table[name] = SymbolInfo(name, kind, tipe, initialized=False)
        return True

    def set_initialized(self, name: str):
        """Marca una variable como inicializada."""
        if self.exists(name):
            self._table[name].initialized = True

    def dump(self):
        """Imprime el contenido de la tabla para debuguear."""
        print("=== Tabla de Símbolos ===")
        for name, info in self._table.items():
            init_flag = "yes" if info.initialized else "no"
            print(f"   {name} : kind={info.kind}, type={info.type}, initialized={init_flag}")
        print("=========================")
