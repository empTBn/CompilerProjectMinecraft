from collections import namedtuple
from parser_tables import (TERMINALES, NUM_T, NUM_NT, EPSILON, TLD, TP, FOLLOW)
from scanner import TokenType

# Un nodo del AST:
# - symbol: nombre del no terminal o terminal
# - children: lista de nodos hijos
# - token: objeto Token (solo para hojas)
Node = namedtuple('Node', ['symbol', 'children', 'token'])


class ParserError(Exception):
    """Error de sintaxis detenido por el parser"""
    pass


class Parser:
    def __init__(self, tokens):
        """
        tokens: lista de Token, incluyendo al final un TokenType.EOF
        """
        self.tokens = tokens
        self.pos = 0
        self.stack = [0]
        self.node_stack = [Node(symbol='S', children=[], token=None)]

    def current(self):
        return self.tokens[self.pos]

    def advance(self):
        self.pos += 1

    def parse(self):
        while True:
            state = self.stack[-1]
            tok = self.current()

            t_code = TERMINALES.get(tok.type.name)
            if t_code is None:
                raise ParserError(f"Token inesperado: {tok.type.name} no está en TERMINALES")

            if state >= len(TLD) or t_code >= len(TLD[state]):
                raise ParserError(f"Índice fuera de rango: estado {state}, t_code {t_code}")

            action = TLD[state][t_code]

            if action == -1:
                raise ParserError(f"Error sintáctico: token {tok.lexeme!r} "
                                  f"({tok.type.name}) en estado {state}")

            elif action == 0:
                parent = self.node_stack[-1]
                eps_node = Node(symbol='ε', children=[], token=None)
                parent.children.append(eps_node)
                self.stack.pop()
                self.node_stack.pop()

            elif action > 0:
                prod = TP[action]
                A = prod[0]
                rhs = prod[1:]

                self.stack.pop()
                parent = self.node_stack.pop()
                A_node = Node(symbol=f'N{A}', children=[], token=None)

                for sym in reversed(rhs):
                    if sym == EPSILON:
                        continue
                    self.stack.append(sym)
                    self.node_stack.append(A_node)

                self.node_stack[-1].children.append(A_node)

            else:
                next_state = -action
                self.stack.append(next_state)
                leaf = Node(symbol=tok.type.name, children=[], token=tok)
                self.node_stack[-1].children.append(leaf)
                self.advance()

            if tok.type == TokenType.EOF and self.stack == [0]:
                break

        root = self.node_stack[0].children[0]
        return root


def parse_tokens(tokens):
    try:
        parser = Parser(tokens)
        tree = parser.parse()
        return []  # sin errores
    except ParserError as e:
        return [str(e)]
