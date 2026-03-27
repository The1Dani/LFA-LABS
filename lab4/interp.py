from dataclasses import dataclass
from lexer import Token, TokenKind, Lexer
from parser import AST, Parser
import random

@dataclass
class Expr:
    value: Token
    tail: Token|None


class Interpreter:

    def __init__(self, ast):
        self.ast: AST = ast

    def interp(self) -> str:
        exprs = ""
        for child in self.ast.childs:
            exprs += self.reduceAndInterp(child)
        return exprs
    
    def reduceAndInterp(self, child: AST):
        
        result = ""

        #OR
        if child.value.kind == TokenKind.OR:
            res: list[str] = []
            for c in child.childs:
                res += self.reduceAndInterp(c)
            result = random.choice(res)
        else:
            result = child.value.value
        #Simple Word
        if child.OP is None:
            return result
        elif child.OP.kind == TokenKind.PLUS:
            return result * random.randint(1, 5)
        elif child.OP.kind == TokenKind.STAR:
            return result * random.randint(0, 5)
        elif child.OP.kind == TokenKind.QUESTION:
            return result * random.randint(0,1)
        elif child.OP.kind == TokenKind.POWER:
            return result * int(child.OP.value)
        else:
            raise ValueError(f"Error expected tokenKind {TokenKind.WORD} got {child.value.kind}")

def findString(program, times=1):
    result = []
    ast = Parser(Lexer(program).lex()).parse()
    interp = Interpreter(ast)
    for _ in range(times):
        result.append(interp.interp())
    return result