from Tokens import *


class Lexer:

    RESERVED_KEYWORDS = [
        ReservedToken(value="=>"),
        ReservedToken(value="do"),
        ReservedToken(value="or"),
        ReservedToken(value="and"),
        ReservedToken(value="else"),
        ReservedToken(value="quasiquote"),
        ReservedToken(value="begin"),
        ReservedToken(value="if"),
        ReservedToken(value="quote"),
        ReservedToken(value="case"),
        ReservedToken(value="lambda"),
        ReservedToken(value="set!"),
        ReservedToken(value="cond"),
        ReservedToken(value="let"),
        ReservedToken(value="unquote"),
        ReservedToken(value="define"),
        ReservedToken(value="let*"),
        ReservedToken(value="unquote"),
        ReservedToken(value="splicing"),
        ReservedToken(value="delay"),
        ReservedToken(value="letrec"),
    ]

    def __init__(self, source: str):
        self.source = source
        self.cursor = 0
        self.line = 0
        self.char = 0

    def new(self, newSource: str):
        return self.__init__(newSource)

    def lex(self) -> list[Token]:

        tokens: list[Token] = []

        while self.cursor < len(self.source):

            # Eat space
            if self.source[self.cursor].isspace():
                self.cursor += 1
                continue

            # SyntaxToken
            token = self._lexSyntaxToken()
            if token:
                tokens.append(token)
                continue

            # IntigerToken
            token = self._lexIntigerToken()
            if token:
                tokens.append(token)
                continue

            # ReservedToken
            token = self._lexReservedToken()
            if token:
                tokens.append(token)
                continue

            # IdentToken
            token = self._lexIdentToken()
            if token:
                tokens.append(token)
                continue

            raise Exception("There was an error")

        return tokens

    def _lexSyntaxToken(self) -> Token | None:
        """
        In scheme lisp there are only two syntax tokens '(' and ')'
        """
        token = None
        t = self.source[self.cursor]
        if t in "()":
            token = Token(TokenKind.LPAR if t == "(" else TokenKind.RPAR)
            self.cursor += 1

        return token

    def _lexIntigerToken(self) -> Token | None:

        origCur = self.cursor
        while self.cursor < len(self.source):
            if self.source[self.cursor] in "0123456789.":
                self.cursor += 1
            else:
                break

        if origCur == self.cursor:
            return None
        else:
            return Token(TokenKind.intigerToken, self.source[origCur : self.cursor])

    def _lexReservedToken(self) -> Token | None:
        origCurs = self.cursor
        ident = self._findIdent()

        if ident in self.RESERVED_KEYWORDS:
            return ReservedToken(value=ident)
        
        self.cursor = origCurs
        return None

    def _lexIdentToken(self) -> Token | None:

        ident = self._findIdent()

        return Token(TokenKind.identToken, ident)

    def _findIdent(self) -> str:
        origCur = self.cursor
        while self.cursor < len(self.source):
            t = self.source[self.cursor]
            if (
                not t.isspace()
                and t not in "()"
            ):
                self.cursor += 1
            else:
                break
        return self.source[origCur : self.cursor]
