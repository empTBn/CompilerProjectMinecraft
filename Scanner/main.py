# ETAPA 1 BIBLIOTECA DE ANÁLISIS LÉXICO
# Emmanuel José Matamoros Jiménez - 2021040420
# Luis Diego Delgado Muñoz - 2020030408

from lexico import InicializarScanner, DemeElSiguienteCaracter, FinalizarScanner

def main():
    # Nombre del archivo para probar la lectura de caracteres
    nombre_archivo = "prueba.txt"

    # Inicializar el scanner con el archivo de prueba
    InicializarScanner(nombre_archivo)

    # Llamar repetidamente a DemeElSiguienteCaracter() hasta llegar al fin de archivo
    while True:
        caracter = DemeElSiguienteCaracter()
        if caracter == 'EOF':
            break
        print(caracter, end='')  # Imprimir el carácter sin salto de línea

    # Liberar los recursos utilizados por el scanner
    FinalizarScanner()

if __name__ == "__main__":
    main()
