$$ Archivo de prueba completo para el analizador léxico de Notch Engine
$$ Incluye todos los componentes del lenguaje para verificar el correcto funcionamiento

WorldName PruebaLexicaCompleta:

$$ Comentario de línea simple
$* Comentario 
   de múltiples
   líneas *$

$$ 1) Palabras reservadas y booleanos
Anvil Bedrock Book CraftingTable Chest
Entity Ghast Inventory Obsidian
PolloCrudo PolloAsado ResourcePack Recipe Rune Repeater
SpawnPoint Stack Spider Shelf Torch
WorldName WorldSave
On Off Is IsNot

$$ 2) Identificadores válidos
_abc ABC123 VarCamel Var_Snake __init__

$$ 3) Números
0;
123456;
007;
3.14159;
0.5;
5.;        $$ parte entera con punto al final
.25;       $$ parte fraccional sin entero
10e3;      $$ notación científica
2.5E-2;

$$ 4) Literales
Char1 = 'a';
CharEsc = '\n';
CharQuote = '\'';
String1 = "Hola, mundo";
StringEsc = "Línea1\nLínea2\tTab";
StringUnterminated = "Esto no cierra

$$ 5) Operadores y comparadores
+ - * // % = < > <= >= == !=

$$ 6) Símbolos
( ) { } [ ] ; : . , @

$$ 7) Ejemplo de programa
WorldName MiMundo:
{
    Repeater i = 0; i < 10; i = i + 1 {
        Inventory SpawnPoint(i) at @player;
    }
    IsNotErrorExample = 1 IsNot 2;
    IsErrorExample    = 1 Is 1;
}

$$ 8) Cadenas y caracteres especiales dentro
Msg = "Comillas: \" Dobles y ' Simples";
Ch  = '\t';

$$ 9) Casos de error y recuperación
$$ Caracteres desconocidos
$ % & @#
$$ Identificador con inicio numérico
9abc
$$ Número mal formado
123..456
$$ Cadena no terminada arriba

$$ 10) Comentario para forzar skip de error
$* comentario mal cerrado...

$$ Fin de pruebas
WorldSave
