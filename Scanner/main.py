from scanner import InicializarScanner, DemeToken, TomeToken, FinalizarScanner, TokenType

def main():
    # Nombre del archivo para probar el scanner
    nombre_archivo = "prueba.ne"

    print(f"Analizando archivo: {nombre_archivo}")
    print("-" * 50)

    # Inicializar el scanner con el archivo de prueba
    InicializarScanner(nombre_archivo)

    # Procesar tokens hasta encontrar EOF
    try:
        while True:
            token = DemeToken()
            print(token)
            
            if token.type == TokenType.EOF:
                break
            
            TomeToken()
    except Exception as e:
        print(f"Error durante el análisis léxico: {e}")
    finally:
        # Liberar los recursos utilizados por el scanner
        FinalizarScanner()

if __name__ == "__main__":
    main()