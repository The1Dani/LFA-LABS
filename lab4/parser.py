from lexer import Token, TokenKind

class AST:

    def __init__(self, value,  OP, parent=None):
        self.parent = parent
        self.childs: list[AST] = []
        self.value: Token = value
        self.OP: Token | None = OP

    def add_leaf(self, value, OP):
        leaf = AST(value, OP, self)
        self.childs.append(leaf)
        return leaf

class Parser:
    """
    PROG = EXPR*
    EXPR = l_par EXPR or EXPR r_par
         | word | EXPR plus | EXPR star
         | EXPR question | EXPR power
    """

    def _ntok(self) -> Token:
        tok = self.tokens[self.cursor]
        self.cursor += 1
        return tok
    
    def _ptok(self) -> Token:
        return self.tokens[self.cursor]

    def __init__(self, tokens):
        self.tokens = tokens
        self.cursor = 0
        self.parseTree = AST(None, False, "PROG")

    def parse(self):
        # PROG = EXPR* 
        while self.cursor < len(self.tokens):
            self._parseExpr(self.parseTree)
        return self.parseTree
    
    def _parseExpr(self, parent: AST):
        tok = self._ntok()

        #WORD Expr = word
        if tok.kind == TokenKind.WORD:
            ntok = self._ptok()
            #TAIL values POWER | QUESTION | STAR | PLUS 
            if ntok.kind in [TokenKind.PLUS, TokenKind.POWER, TokenKind.STAR, TokenKind.QUESTION]:
                self._ntok()
                parent.add_leaf(tok, ntok)
            else:
                parent.add_leaf(tok, None)
            return
        
        if tok.kind != TokenKind.LPAR:
            raise ValueError(f"Invalid expr with invalid token = {tok}")
        
        # '(' EXPR (| EXPR)+ ')'
        leaf = parent.add_leaf(Token(TokenKind.OR), None)
        # L_PAR already consumed in the first
        self._parseExpr(leaf)
        self._consume(TokenKind.OR)
        self._parseExpr(leaf)
        
        while self._ptok().kind == TokenKind.OR:
            self._consume(TokenKind.OR)
            self._parseExpr(leaf)
        
        self._consume(TokenKind.RPAR)

        ntok = self._ptok()
        if ntok.kind in [TokenKind.PLUS, TokenKind.POWER, TokenKind.STAR, TokenKind.QUESTION]:
            self._ntok()
            leaf.OP = ntok


    def _consume(self, tok_kind):
        tok = self._ntok()
        if tok.kind != tok_kind:
            raise ValueError(f"Invalid expr with invalid token = {tok}, expected token kind {tok_kind}")
        return tok