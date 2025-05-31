from scanner import InicializarScanner, DemeToken, TomeToken, FinalizarScanner, TokenType
from parser import parse_tokens

def lex_file(nombre_archivo: str):
    """
    Recorre todo el archivo y devuelve la lista completa de tokens.
    """
    tokens = []
    InicializarScanner(nombre_archivo)
    try:
        while True:
            tok = DemeToken()
            tokens.append(tok)
            if tok.type == TokenType.EOF:
                break
            TomeToken()
    finally:
        FinalizarScanner()
    return tokens

def main():
    archivo = "prueba.ne"

    # Fase léxica: se obtiene el listado completo de tokens
    tokens = lex_file(archivo)
    print(f"Tokens obtenidos ({len(tokens)}):")
    for t in tokens:
        print("  ", t)
    print()

    # Fase sintáctica: alimentamos el parser con la lista de tokens
    print(f"Iniciando parser sobre los {len(tokens)} tokens...\n")
    errores = parse_tokens(tokens)
    if errores:
        print("\nErrores sintácticos detectados:")
        for e in errores:
            print("  -", e)
    else:
        print("Parseo completado sin errores.")

if __name__ == "__main__":
    main()
