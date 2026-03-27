from enum import StrEnum
from dataclasses import dataclass


class TokenKind(StrEnum):
    LPAR = "L_PAR"
    RPAR = "R_PAR"
    WORD = "WORD"
    PLUS = "PLUS"
    OR = "OR"
    STAR = "STAR"
    QUESTION = "QUESTION"
    POWER = "POWER"

@dataclass
class Token:
    kind: TokenKind
    value: str | None = None

    def __str__(self):
        val = self.value if self.value is not None else ""
        return f"{self.kind}({val})"


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.cursor = 0

    def nchar(self):
        """Consume next char"""
        char = self.source[self.cursor]
        self.cursor += 1
        return char

    def pchar(self):
        """Peek at next char"""
        return self.source[self.cursor]

    def lex(self) -> list[Token]:
        tokens: list[Token] = []

        while self.cursor < len(self.source):

            # Parents
            token = self._lexParent()
            if token:
                tokens.append(token)
                continue

            # Pipe
            if self.pchar() == "|":
                self.nchar()
                tokens.append(Token(TokenKind.OR))
                continue

            # Question
            if self.pchar() == "?":
                self.nchar()
                tokens.append(Token(TokenKind.QUESTION))
                continue

            # Power | + | *
            if self.pchar() == "^":
                self.nchar()
                token = self._lexPPS()
                if not token:
                    raise ValueError("Wrong Power Token")
                tokens.append(token)
                continue

            # IdentToken
            token = self._lexWord()
            if token:
                tokens.append(token)
                continue

            raise Exception("There was an error")

        return tokens

    def _lexPPS(self):
        char = self.nchar()
        if char == "+":
            return Token(TokenKind.PLUS)
        if char == "*":
            return Token(TokenKind.STAR)
        if char.isdigit():
            return Token(TokenKind.POWER, char)

    def _lexParent(self):

        char = self.source[self.cursor]
        if char == "(":
            self.cursor += 1
            return Token(TokenKind.LPAR)
        if char == ")":
            self.cursor += 1
            return Token(TokenKind.RPAR)

        return None

    def _lexWord(self) -> Token | None:

        ident = self._findWord()

        return Token(TokenKind.WORD, ident)

    def _findWord(self) -> str:
        origCur = self.cursor
        while self.cursor < len(self.source):
            t = self.source[self.cursor]
            if not t.isspace() and t not in "()?|^":
                self.cursor += 1
            else:
                break
        return self.source[origCur : self.cursor]
