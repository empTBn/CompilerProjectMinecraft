from scanner import InicializarScanner, DemeToken, TomeToken, FinalizarScanner, TokenType
from parser import Parser, ParserError
from parser_tables import TERMINALES 


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
    archivo = "prueba2.ne"

    tokens = lex_file(archivo)
    print(f"Tokens obtenidos ({len(tokens)}):")
    for t in tokens:
        print("  ", t)
    print()

    print(f"Iniciando parser sobre los {len(tokens)} tokens...\n")

    # ✅ Solo tokens válidos para el parser
    tokens_filtrados = [t for t in tokens if t.type.name in TERMINALES]

    try:
        parser = Parser(tokens_filtrados)
        ast = parser.parse()
        print("Parseo completado sin errores.")

        def imprimir_ast(nodo, indent=0):
            print("  " * indent + str(nodo.symbol))
            for hijo in nodo.children:
                imprimir_ast(hijo, indent + 1)

        print("\nÁrbol sintáctico:")
        imprimir_ast(ast)

    except ParserError as e:
        print("Error de sintaxis durante el parseo:")
        print("  -", str(e))

if __name__ == "__main__":
    main()
