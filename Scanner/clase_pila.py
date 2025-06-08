# type_stack.py

class TypeStack:
    """
    Pila auxiliar de tipos. En el análisis semántico se usa para:
      - apilar el tipo de un literal (p.ej. “int” para INT_LIT, “string” para STRING_LIT)
      - apilar el tipo de una variable (con base en SymbolTable.lookup)
      - al reducir operadores binarios, remover dos tipos y verificar compatibilidad.
    """
    def __init__(self):
        self._data = []

    def push(self, tipe: str):
        self._data.append(tipe)

    def pop(self) -> str:
        return self._data.pop() if self._data else None

    def top(self) -> str:
        return self._data[-1] if self._data else None

    def is_empty(self) -> bool:
        return not self._data

    def pop_and_check_binary_op(self, operator: str) -> bool:
        """
        Ejemplo de verificación si los dos tope son compatibles
        con un operador binario (p.ej. “+” acepta (“int”, “int”) solo).
        - operator: cadena “+” o “-” o “=”, etc.
        Devuelve True si OK, False si no.
        Remueve dos tipos y apila el resultado (si es correcto).
        """
        if len(self._data) < 2:
            return False
        right = self.pop()
        left = self.pop()

        if operator in ["+", "-", "*", "/"]:
            # Solo int+int → int
            if left == "int" and right == "int":
                self.push("int")
                return True
            else:
                return False
        elif operator == "=":
            # Asignación: left debe ser variable (se asume que verificamos antes)
            # y right debe coincidir con left
            if left == right:
                self.push(left)
                return True
            else:
                return False
        # …otros operadores posibles…
        return False
