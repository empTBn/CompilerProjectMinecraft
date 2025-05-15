$$ Archivo de prueba completo para el analizador léxico de Notch Engine
$$ Incluye todos los componentes del lenguaje para verificar el correcto funcionamiento

WorldName PruebaLexicaCompleta:

$$ Comentario de línea simple
$* Comentario 
   de múltiples
   líneas *$

$$ Sección de constantes
Bedrock MAX_ITEMS = 64;
Bedrock MIN_LEVEL = 1;
Obsidian Stack PI_ENTERO = 3;
Obsidian Ghast PI_EXACTO = 3.14159;

$$ Sección de tipos
ResourcePack:
    MiTipo: Stack
    MiRegistro: Entity
    MiLista: Shelf
    MiConjunto: Chest

$$ Sección de variables
Inventory;
    $$ Variables con tipos básicos
    Stack contador = 0;
    Stack contador_hex = 0x1F;  $$ Hexadecimal
    Stack contador_oct = 075;   $$ Octal
    Spider mensaje = "¡Hola mundo!";
    Spider mensaje_escape = "Texto con \"escape\"";
    Torch bandera = On;
    Torch otra_bandera = Off;
    Rune simbolo = 'A';
    Rune simbolo_escape = '\n';
    Ghast pi = 3.14159;
    
    $$ Estructuras de datos
    Chest vocales = {: 'a', 'e', 'i', 'o', 'u' :};
    Shelf herramientas = ["pico", "hacha", "pala"];
    Entity jugador = {nombre: "Steve", nivel: 10, salud: 20};
    Book archivo = {/ "datos.txt", 'L' /};

$$ Sección de rutinas
CraftingTable

$$ Definición de procedimiento
Ritual Saludar(Spider :: nombre, edad; Stack ref nivel);

$$ Definición de función
Spell Calcular(Ghast :: x, y) -> Ghast;

$$ Punto de entrada del programa
SpawnPoint

    $$ Declaraciones y asignaciones
    Stack a = 10;
    Stack b = 5;
    Ghast c = 3.5;
    
    $$ Operaciones aritméticas de enteros
    Stack suma = a + b;
    Stack resta = a - b;
    Stack multiplicacion = a * b;
    Stack division = a // b;
    Stack modulo = a % b;
    
    $$ Operaciones con flotantes
    Ghast suma_f = c :+ 1.5;
    Ghast resta_f = c :- 0.5;
    Ghast mult_f = c :* 2.0;
    Ghast div_f = c :// 2.0;
    Ghast mod_f = c :% 1.0;
    
    $$ Operaciones de incremento/decremento
    soulsand a;  $$ Incremento
    magma b;     $$ Decremento
    
    $$ Operaciones de asignación compuesta
    a += 5;
    b -= 2;
    suma *= 2;
    division //= 2;
    modulo %= 2;
    
    $$ Operaciones de comparación
    Torch comp1 = a < b;
    Torch comp2 = a > b;
    Torch comp3 = a <= b;
    Torch comp4 = a >= b;
    Torch comp5 = a is b;
    Torch comp6 = a isNot b;
    
    $$ Operaciones lógicas
    Torch res1 = comp1 and comp2;
    Torch res2 = comp3 or comp4;
    Torch res3 = not comp5;
    Torch res4 = comp1 xor comp6;
    
    $$ Operaciones con strings
    Spider nombre = "Steve";
    Spider saludo = "Hola " bind nombre;
    Stack longitud = #saludo;
    Spider subcadena = saludo from 0 ## 4;
    Spider recortada = saludo except 5 ## 5;
    Stack posicion = saludo seek "Steve";
    
    $$ Operaciones con caracteres
    Rune letra = 'A';
    Torch es_letra = isEngraved letra;
    Torch es_digito = isInscribed letra;
    Rune mayuscula = etchUp 'a';
    Rune minuscula = etchDown 'A';
    
    $$ Operaciones con conjuntos
    Chest numeros = {: 1, 2, 3 :};
    add numeros, 4;
    drop numeros, 2;
    Chest mas_numeros = {: 3, 4, 5 :};
    Chest union = feed numeros, mas_numeros;
    Chest interseccion = map numeros, mas_numeros;
    Torch pertenece = biom 3, numeros;
    Torch esta_vacio = void numeros;
    
    $$ Acceso a elementos
    Rune primera_letra = nombre[0];
    Stack primera_herramienta = herramientas[0];
    Spider nombre_jugador = jugador@nombre;
    
    $$ Estructura de control if-then-else
    target a > b craft
        hit
            dropper"a es mayor que b";
        miss
            dropper"a no es mayor que b";
    
    $$ Estructura de control while
    repeater contador < 5 craft
        dropper"Contador: ";
        droppercontador;
        contador += 1;
    
    $$ Estructura de control for
    walk i set 0 to 5 step 1 craft
        dropper"Valor de i: ";
        dropperStack i;
    
    $$ Estructura repeat-until
    spawner
        dropper"Decremento: ";
        magma contador;
        droppercontador;
    exhausted contador <= 0;
    
    $$ Estructura switch
    jukebox contador craft
        disc 0:
            dropper"Contador es cero";
        disc 1:
            dropper"Contador es uno";
        silence:
            dropper"Otro valor";
    
    $$ Estructura with
    wither jugador craft
        dropper@nombre;
        @nivel += 1;
    
    $$ Instrucciones de control de flujo
    target contador is 0 craft
        hit
            respawn 0;
    
    $$ Instrucciones break y continue
    repeater contador < 10 craft
        contador += 1;
        target contador is 5 craft
            hit
                enderPearl;
        target contador is 9 craft
            hit
                creeper;
    
    $$ Operaciones de E/S
    dropper"Ingrese un número: ";
    Stack num_ingresado = hopperStack();
    
    $$ Operaciones de archivos
    unlock archivo;
    gather archivo;
    forge archivo, "Datos de prueba";
    lock archivo;
    
    $$ Conversión de tipos
    Stack entero = c >> Stack;
    
    $$ Operaciones de tamaño
    Stack tam_stack = chunk Stack;
    Stack tam_var = chunk contador;
    
    $$ Instrucción halt
    target a > 100 craft
        hit
            ragequit;
    
    $$ Instrucciones de bloque
    PolloCrudo
        dropper"Inicio del bloque";
        Stack local = 10;
        dropper"Fin del bloque";
    PolloAsado

$$ Fin del programa
worldSave