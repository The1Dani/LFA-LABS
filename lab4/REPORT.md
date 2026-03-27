# Lexer & Scanner

### Course: Formal Languages & Finite Automata
### Author: Daniel Canter FAF-242

----

## Objectives:

1. Write a code that will generate valid combinations of symbols conform given regular expressions (examples will be shown). Be careful that idea is to interpret the given regular expressions dinamycally, not to hardcode the way it will generate valid strings. You give a set of regexes as input and get valid word as an output

2. In case you have an example, where symbol may be written undefined number of times, take a limit of 5 times (to evade generation of extremely long combinations);

## Implementation description

In this laboratory work we use a lexer to transform the program into tokens and then using a parser into an AST. After we get an AST we can traverse it and interpret it at the same time.


### lexer.py

In this file we define our main class of interest **Lexer** we start with defining the keywords in a list. Then in the constructor of the class we have to set two important class attributes source and cursor. A lexer basically goes through the text and finds the keywords of interest and only if the keyword is valid for the case it **consumes** it meaning it will increment the cursor.

```py
def lex(self) -> list[Token]:
    tokens: list[Token] = []

    while self.cursor < len(self.source):

        # Parents
        token = self._lexParent()
        if token:
            tokens.append(token)
            continue

        # Pipe
        # pchar is peek_char // gets the char without consuming
        # nchar is next_char // gets the char while consuming it
        if self._pchar() == "|":
            self._nchar()
            tokens.append(Token(TokenKind.OR))
            continue

        # Question
        if self._pchar() == "?":
            self._nchar()
            tokens.append(Token(TokenKind.QUESTION))
            continue

        # Power | + | *
        if self._pchar() == "^":
            self._nchar()
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
```

As you can see from the our main method of our class **lex** we have a list **tokens** and an loop that continues as long as our **cursor** is in the bounds of **source**. This is important because we want to catch all tokens until the end of our program **source**. On each iteration we find a token and we continue the loop maybe the most used continue in this loop is the first case of consuming the spaces.

```py
def _findWord(self) -> str:
    origCur = self.cursor
    while self.cursor < len(self.source):
        t = self.source[self.cursor]
        if not t.isspace() and t not in "()?|^":
            self.cursor += 1
        else:
            break
    return self.source[origCur : self.cursor]
```

the method you see above is probably the most interesting of them all and its used to find a word token for other functions a.k.a its a helper function. This method checks if the character is not a space character and if its not any kind of syntax token it spits out the token that it has found in the process consuming the token from the stream.

### parser.py
In this file we define a **Parser** implementation alongside a very simple **AST**:
```py
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
```
And we do parsing with Parser using the method
```py
def parse(self):
    # PROG = EXPR* 
    while self.cursor < len(self.tokens):
        self._parseExpr(self.parseTree)
    return self.parseTree```
```
```py
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
    leaf = parent.add_leaf(Token(TokenKind.OR), None) #Create a new OR leaf
    # L_PAR already consumed in the first
    self._parseExpr(leaf)
    self._consume(TokenKind.OR)
    self._parseExpr(leaf)
    
    while self._ptok().kind == TokenKind.OR:
        self._consume(TokenKind.OR)
        self._parseExpr(leaf)
    
    self._consume(TokenKind.RPAR)
    
    #TAIL values for the grouped OR, POWER | QUESTION | STAR | PLUS 
    ntok = self._ptok()
    if ntok.kind in [TokenKind.PLUS, TokenKind.POWER, TokenKind.STAR, TokenKind.QUESTION]:
        self._ntok()
        leaf.OP = ntok
```

The parse method calls the parseExpr method as long as there are more new tokens to process.
The way we parse the program is that we have two main kinds of expressions one is a WORD and the other is an OR both of them gets themselvs a potantial tail which are operations that will be applied to them. After the parsing is finished and we get to Interpretation.

### iterp.py

So in the interpreter our job is even simpler we need to go trough the ast and find a string.

```py
class Interpreter:

    def __init__(self, ast):
        self.ast: AST = ast

    def interp(self) -> str:
        exprs = ""
        for child in self.ast.childs:
            exprs += self._reduceAndInterp(child)
        return exprs
    
    def _reduceAndInterp(self, child: AST):
        
        result = ""

        #OR
        if child.value.kind == TokenKind.OR:
            res: list[str] = []
            for c in child.childs:
                res += self._reduceAndInterp(c)
            result = random.choice(res)
        #Simple Word
        else:
            result = child.value.value
        
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
```

Surprisingly this is the whole class. How we Interpret the **AST** is really similar to how we parsed it. There are two cases if we find a WORD we get its value and then if it has an associate operation we apply the operation to that word and we return it. The other case is is practically the same but instead of getting the value of the OR we go down the tree recursively and then choose one of the results randomly. And finnaly look if it has some operation and compute if it has and thats all. One more thing in main i used **findString** function which is an abstraction over all of the stuff and generates a string over a program string.

```py
def findString(program, times=1):
    result = []
    ast = Parser(Lexer(program).lex()).parse()
    interp = Interpreter(ast)
    for _ in range(times):
        result.append(interp.interp())
    return result
``` 

### main.py
```py
from interp import findString

if __name__ == "__main__":
    # Variant 2
    programs = [
        "M?N^2(O|P)^3Q^*R^+",
        "(X|Y|Z)^38^+(9|O)^2",
        "(H|i)(J|K)L^*N?",
    ]

    for prog in programs:
        result = findString(prog, 5)

        print(result)

```
We compute our variant and thats it.


## Conclusion

In this laboratory work we used a lexer to get the lexical composition of the program. A parser to parse the lexical representation of the program in order to put meaning and scope.
An interpreter which looked into the AST and found us a string while unwrapping OR operations recursively. At the end we used the power of the abstraction to have a very simple interface to interact with our program.

  