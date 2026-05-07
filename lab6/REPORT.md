# Parser & Building an Abstract Syntax Tree

### Course: Formal Languages & Finite Automata

### Author: Daniel Canter FAF-242

---

## Objectives:

1 - Implement the necessary data structures for an AST that could be used for the text you have processed in the 3rd lab work.
2 - Implement a simple parser program that could extract the syntactic information from the input text.

## Implementation description

In this laboratory work we use a lexer to transform the program text into tokens and then using a parser to build a parse tree. After we get a parse tree we can display it in a tree-like format.

### Tokens.py

In this file we define our token kinds and the Token classes. We have an enum **TokenKind** which contains all possible token types: LPAR, RPAR, identToken, intigerToken, reservedToken, trueToken, falseToken, stringToken.

```py
class TokenKind(StrEnum):
    LPAR = "L_PAR"
    RPAR = "R_PAR"
    identToken = "IDENT"
    intigerToken = "INTIGER"
    reservedToken = "RESERVED"
    trueToken = "TRUE"
    falseToken = "FALSE"
    stringToken = "STRING"
```

We also have a Token dataclass that holds the kind and optional value, and a ReservedToken class for keywords.

### lexer.py

In this file we define our main class **Lexer** that transforms the source code into a list of tokens. We start by defining reserved keywords in a list including "define", "if", "set!", "lambda", "and", "or", "let", "cond", "quote", and many more.

```py
RESERVED_KEYWORDS = [
    ReservedToken(value="=>"),
    ReservedToken(value="do"),
    ReservedToken(value="or"),
    # ... etc
]
```

The main method of the class is **lex** which returns a list of tokens:

```py
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
        # ... etc
```

The lexer processes tokens in a specific order: spaces, syntax tokens (parentheses), integers, reserved keywords, booleans, strings, and finally identifiers. Each helper method tries to lex a specific type of token and returns None if it fails, allowing the lexer to try the next type.

The most important helper method is **\_findIdent** which extracts an identifier or word from the source:

```py
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
```

This method keeps advancing the cursor as long as it finds non-whitespace characters that are not parentheses.

### parser.py

In this file we define the **Parser** class which builds a parse tree from the token stream. We also define several enums for tracking parsing rules and node types:

```py
class ParseRule(Enum):
    EMPTY = auto()
    PROGRAM = auto()
    EXPR = auto()
    ATOM = auto()
    SPECIAL_FORM = auto()
    LIST = auto()
    QUOTED = auto()
    TERMINAL = auto()
```

The **ParseTree** class represents a node in our parse tree with a parent reference, a list of child elements, a value, and a rule:

```py
class ParseTree:
    def __init__(self, rule: Enum, parent: ParseTree):
        self.parent = parent
        self.elements: list[ParseTree] = []
        self.value = None
        self.rule = rule
```

The parser has a **parse** method which creates a root node and calls parseProgram:

```py
def parse(self):
    root = ParseTree(ParseRule.PROGRAM, None)
    return self.parseProgram(root)
```

The parseProgram method continues parsing expressions until it returns None:

```py
def parseProgram(self, parent: ParseTree) -> ParseTree:
    while True:
        expr = self.parseExpr()
        if expr is None:
            break
        parent.pushElement(expr)
    return parent
```

The **parseExpr** method tries to parse different types of expressions in order: atoms, special forms, lists, and quoted expressions:

```py
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
```

The **parseList** method handles parsing of lists enclosed in parentheses:

```py
def parseList(self) -> ParseTree | None:
    list_ = ParseTree(ParseRule.LIST, None)
    startCursor = self.cursor

    lpar = self.getTyped(TokenKind.LPAR)
    if lpar is None:
        self.cursor = startCursor
        return None

    while True:
        expr = self.parseExpr()
        if expr is None:
            break
        list_.pushElement(expr)

    rpar = self.getTyped(TokenKind.RPAR)
    if rpar is None:
        self.cursor = startCursor
        return None

    return list_
```

The **parseSpecialForm** method handles special forms like define, if, set!, and lambda:

```py
def parseSpecialForm(self) -> ParseTree | None:
    start_cursor = self.cursor
    special_form = None

    lpar = self.getTyped(TokenKind.LPAR)
    if lpar is None:
        self.cursor = start_cursor
        return None

    special_token = self.getTyped(TokenKind.reservedToken)
    if special_token and special_token.value in special_tokens:
        ttype = special_tokens[special_token.value]
        special_form = self.parseSpecialFormType(ttype)

    rpar = self.getTyped(TokenKind.RPAR)
    if rpar is None:
        self.cursor = start_cursor
        return None

    if special_form is None:
        self.cursor = start_cursor
        return None

    return special_form
```

The **parseSpecialFormType** method dispatches to specific parsers based on the special form type:

```py
def parseSpecialFormType(self, ttype: SpecialForm) -> ParseTree | None:
    special_form = ParseTree(ttype, None)
    start_cursor = self.cursor

    if ttype in [SpecialForm.DEFINE, SpecialForm.SET_BANG]:
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
        exprs = []
        for _ in range(3):
            exprs.append(self.parseExpr())
        # ... handle if special form

    elif ttype == SpecialForm.LAMBDA:
        list = self.parseList()
        body_expr = self.parseExpr()
        # ... handle lambda special form
```

The parse tree has a **display** method that prints it in a tree format using branch symbols:

```py
def display(self, prefix: str = "", is_last: bool = True, is_root: bool = True) -> None:
    if is_root:
        print(repr(self))
    else:
        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{repr(self)}")

    # Recursively display children
    for i, child in enumerate(self.elements):
        last_child = (i == len(self.elements) - 1)
        child.display(new_prefix, last_child, is_root=False)
```

### main.py

```py
from lexer import Lexer
from parser import Parser


def main() -> None:
    prog = """
        (define a 12)
        (define b 12)
        (+ a b)
        """
    lexed = Lexer(prog).lex()

    parser = Parser(lexed)

    parse_tree = parser.parse()

    parse_tree.display()

if __name__ == "__main__":
    main()
```

We define a simple program with define statements and a function call, then lex it, parse it, and display the parse tree. The parser builds a tree structure representing the syntactic structure of the program.

## Conclusion

In this laboratory work we implemented a lexer to tokenize the Scheme-like source code into meaningful tokens including identifiers, integers, reserved keywords, booleans, and strings. We then built a parser that constructs a parse tree by recursively processing expressions, lists, special forms, and quoted expressions. The final parse tree is displayed in a tree format showing the hierarchical structure of the program. This implementation demonstrates the fundamental concepts of lexical analysis and syntactic analysis in compiler design.
