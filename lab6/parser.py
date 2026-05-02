from Tokens import TokenKind, Token

from enum import Enum, auto


class ParseRule(Enum):
    EMPTY = auto()
    PROGRAM = auto()
    EXPR = auto()
    ATOM = auto()
    SPECIAL_FORM = auto()
    LIST = auto()
    QUOTED = auto()
    TERMINAL = auto()


class Terminal(Enum):
    IDENTIFIER = auto()
    NUMBER = auto()
    BOOLEAN = auto()
    STRING = auto()
    KEYWORD = auto()


class SpecialForm(Enum):
    DEFINE = auto()
    IF_COND = auto()
    SET_BANG = auto()
    LAMBDA = auto()


terminals = {
    TokenKind.identToken: Terminal.IDENTIFIER,
    TokenKind.intigerToken: Terminal.NUMBER,
    TokenKind.trueToken: Terminal.BOOLEAN,
    TokenKind.falseToken: Terminal.BOOLEAN,
    TokenKind.stringToken: Terminal.STRING,
}

special_tokens = {
    "define": SpecialForm.DEFINE,
    "if": SpecialForm.IF_COND,
    "set!": SpecialForm.SET_BANG,
    "lambda": SpecialForm.LAMBDA,
}


class ParseTree:
    def __init__(self, rule: Enum, parent: ParseTree):
        self.parent = parent
        self.elements: list[ParseTree] = []
        self.value = None
        self.rule = rule

    def pushElement(self, el: ParseTree) -> None:
        el.parent = self
        self.elements.append(el)

    def pushNew(self, rule: Enum) -> ParseTree:
        child = ParseTree(rule, self)
        self.pushElement(child)
        return child

    def __repr__(self):
        return f"{self.rule}({self.value})"

    def display(self, prefix: str = "", is_last: bool = True, is_root: bool = True) -> None:
        if is_root:
            # Print the root node without any branch symbols
            print(repr(self))
        else:
            # Use branch symbols for all children
            connector = "└── " if is_last else "├── "
            print(f"{prefix}{connector}{repr(self)}")
        
        # Adjust prefix for children
        # If we were the root, we don't add extra indentation yet
        if is_root:
            new_prefix = ""
        else:
            new_prefix = prefix + ("    " if is_last else "│   ")
        
        num_elements = len(self.elements)
        for i, child in enumerate(self.elements):
            last_child = (i == num_elements - 1)
            # All subsequent calls are not the root
            child.display(new_prefix, last_child, is_root=False)

class Parser:

    def __init__(self, tokenStream):
        self.stream: list[Token] = tokenStream
        self.cursor = 0

    def parse(self):
        root = ParseTree(ParseRule.PROGRAM, None)
        return self.parseProgram(root)

    def parseProgram(self, parent: ParseTree) -> ParseTree:
        while True:
            expr = self.parseExpr()
            if expr is None:
                break
            parent.pushElement(expr)
        return parent

    def parseExpr(self) -> ParseTree | None:

        expr = ParseTree(ParseRule.EXPR, None)

        atom = self.parseAtom()
        if atom is not None:
            expr.pushElement(atom)
            return expr

        special_form = self.parseSpecialForm()
        if special_form is not None:
            expr.pushElement(special_form)
            return expr

        list_ = self.parseList()
        if list_ is not None:
            expr.pushElement(list_)
            return expr

        quoted = self.parseQuoted()
        if quoted is not None:
            expr.pushElement(quoted)
            return expr

        return None

    def parseQuoted(self) -> ParseTree | None:

        startCursor = self.cursor

        q = ParseTree(ParseRule.QUOTED, None)

        # "'"
        quote = self.getTyped(TokenKind.reservedToken)
        if quote is None:
            self.cursor = startCursor
            return None
        if quote.value != "'":
            self.cursor = startCursor
            return None

        kw = ParseTree(Terminal.KEYWORD, None)
        kw.value = quote.value

        q.pushElement(kw)

        # expr
        expr = self.parseExpr()
        if expr is None:
            self.cursor = startCursor
            return None

        q.pushElement(expr)

        return q

    def parseList(self) -> ParseTree | None:

        list_ = ParseTree(ParseRule.LIST, None)

        startCursor = self.cursor

        # '('
        lpar = self.getTyped(TokenKind.LPAR)
        if lpar is None:
            self.cursor = startCursor
            return None

        # expr*
        while True:
            expr = self.parseExpr()
            if expr is None:
                break
            list_.pushElement(expr)

        # ')'
        rpar = self.getTyped(TokenKind.RPAR)
        if rpar is None:
            self.cursor = startCursor
            return None

        return list_

    def parseSpecialForm(self) -> ParseTree | None:
        """
            special_form
        : '(' DEFINE variable expression ')'
        | '(' IF test=expression then=expression else_=expression ')'
        | '(' SET_BANG variable expression ')'
        | '(' LAMBDA '(' variable* ')' body=expression ')'
        ;
        """
        start_cursor = self.cursor
        special_form = None

        # '('
        lpar = self.getTyped(TokenKind.LPAR)
        if lpar is None:
            self.cursor = start_cursor
            return None

        special_token = self.getTyped(TokenKind.reservedToken)
        if special_token and special_token.value in special_tokens:
            ttype = special_tokens[special_token.value]

            # If not valid its going to return None
            special_form = self.parseSpecialFormType(ttype)

        else:
            self.cursor = start_cursor
            return None

        # ')'
        rpar = self.getTyped(TokenKind.RPAR)
        if rpar is None:
            self.cursor = start_cursor
            return None

        # If not special case
        if special_form is None:
            self.cursor = start_cursor
            return None

        return special_form

    def parseVariable(self) -> ParseTree | None:
        start = self.cursor
        if self.getTyped(TokenKind.identToken):
            self.cursor = start
            return self.parseAtom()

        self.cursor = start
        return None

    def parseSpecialFormType(self, ttype: SpecialForm) -> ParseTree | None:

        special_form = ParseTree(ttype, None)
        start_cursor = self.cursor

        if ttype in [SpecialForm.DEFINE, SpecialForm.SET_BANG]:
            #'(' DEFINE variable expression ')'
            ident = self.parseVariable()
            if ident is None:
                self.cursor = start_cursor
                return None
            special_form.pushElement(ident)

            expr = self.parseExpr()
            if expr is None:
                self.cursor = start_cursor
                return None
            special_form.pushElement(expr)

        elif ttype == SpecialForm.IF_COND:
            #'(' IF expr^2 expr? ')'
            exprs = []
            for _ in range(3):
                exprs.append(self.parseExpr())

            # if the first 2 elements are not expr
            if not all(expr is None for expr in exprs[:2]):
                self.cursor = start_cursor
                return None

            for expr in filter(lambda expr: expr is not None, exprs):
                special_form.pushElement(expr)

        elif ttype == SpecialForm.LAMBDA:
            # '(' LAMBDA list expr ')'

            list = self.parseList()
            if list is None:
                self.cursor = start_cursor
                return None
            special_form.pushElement(list)

            body_expr = self.parseExpr()
            if body_expr is None:
                self.cursor = start_cursor
                return None
            special_form.pushElement(body_expr)

        else:
            return None
        return special_form

    def parseAtom(self) -> ParseTree | None:
        atom = ParseTree(ParseRule.ATOM, None)

        tok = self.peekNext()
        if tok is None:
            return None

        if tok.kind in [
            TokenKind.identToken,
            TokenKind.intigerToken,
            TokenKind.trueToken,
            TokenKind.falseToken,
            TokenKind.stringToken,
        ]:
            self.getNext()
            child = ParseTree(terminals[tok.kind], None)
            child.value = tok
            atom.pushElement(child)
            return atom

        return None

    def getNext(self) -> Token | None:
        tok = self.peekNext()
        if tok is None:
            return None
        self.cursor += 1
        return tok

    def peekNext(self) -> Token | None:
        if self.cursor >= len(self.stream):
            return None
        return self.stream[self.cursor]

    def getTyped(self, kind: TokenKind) -> Token | None:

        tok = self.getNext()
        if tok is None:
            return None
        if tok.kind != kind:
            return None
        return tok
