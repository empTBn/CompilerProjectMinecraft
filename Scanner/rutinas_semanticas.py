from tabla_simbolos import SymbolTable
from clase_pila import TypeStack

symtab = SymbolTable()
typestack = TypeStack()

def declare_variable(name: str, lineno: int) -> None:
    if not symtab.insert(name, kind="var", tipe="int"):
        print(f"[SEMANTIC ERROR] Línea {lineno}: Variable '{name}' ya declarada.")

def check_variable_exists(name: str, lineno: int) -> None:
    if not symtab.exists(name):
        print(f"[SEMANTIC ERROR] Línea {lineno}: Variable '{name}' no declarada.")

def mark_variable_initialized(name: str) -> None:
    symtab.set_initialized(name)

def push_literal_type(token) -> None:
    if token.type == token.INT_LIT:
        typestack.push("int")
    elif token.type == token.STRING_LIT:
        typestack.push("string")
    else:
        typestack.push("unknown")

def push_variable_type(token) -> None:
    info = symtab.lookup(token.lexeme)
    if info is None:
        print(f"[SEMANTIC ERROR] Línea {token.line}: Variable '{token.lexeme}' no declarada.")
        typestack.push("error")
    else:
        typestack.push(info.type)

def check_assignment_types(left_token, right_token) -> None:
    info_left = symtab.lookup(left_token.lexeme)
    if info_left is None:
        print(f"[SEMANTIC ERROR] Línea {left_token.line}: Variable '{left_token.lexeme}' no declarada.")
        return

    if right_token.type == right_token.INT_LIT:
        right_type = "int"
    elif right_token.type == right_token.STRING_LIT:
        right_type = "string"
    elif right_token.type == right_token.ID:
        info_r = symtab.lookup(right_token.lexeme)
        if info_r is None:
            print(f"[SEMANTIC ERROR] Línea {right_token.line}: Variable '{right_token.lexeme}' no declarada.")
            return
        right_type = info_r.type
    else:
        right_type = "unknown"

    if info_left.type != right_type:
        print(
            f"[SEMANTIC ERROR] Línea {left_token.line}: "
            f"No coincide el tipo en asignación: '{info_left.type}' ≠ '{right_type}'."
        )
    else:
        mark_variable_initialized(left_token.lexeme)

def dump_symbol_table():
    symtab.dump()
