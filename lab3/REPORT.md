# Lexer & Scanner

### Course: Formal Languages & Finite Automata
### Author: Daniel Canter FAF-242

----

## Objectives:

1. Understand what lexical analysis is.
2. Get familiar with the inner workings of a lexer/scanner/tokenizer.
3. Implement a sample lexer and show how it works.

## Implementation description

In this laboratory work my goal was to implement a lexer for the famous and old programming language Scheme Lisp [1].

### Tokens.py

In this file i defined some usefull types that ill use in the lexer. 

We define three types TokenKind which is an enum for our token names. Token and ReservedToken. I chose Reserved Token to be a variant of token and it overriding the **_\_str__** and **_\_eq__** methods to represent it differently in some cases. This ReservedToken is nothing else then a keyword and i wanted to represent all keywords in one enum value and class.

### lexer.py

In this file we define our main class of interest **Lexer** we start with defining the keywords in a list. Then in the constructor of the class we have to set two important class attributes source and cursor. A lexer basically goes through the text and finds the keywords of interest and only if the keyword is valid for the case it **consumes** it meaning it will increment the cursor.

```py
def lex(self) -> list[Token]:

    tokens: list[Token] = []

    while self.cursor < len(self.source):

        # Consume space
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
```

As you can see from the our main method of our class **lex** we have a list **tokens** and an loop that continues as long as our **cursor** is in the bounds of **source**. This is important because we want to catch all tokens until the end of our program **source**. On each iteration we find a token and we continue the loop maybe the most used continue in this loop is the first case of consuming the spaces. Because the spaces are unimportant to our languange we just consume them right away. After the fact we go through all possible types of tokens we can have and check if the next series of characters is a token. In the ancient language of Scheme almost anything can be identifier and if it cant its probably another token so you need to try really hard to trip the lexer or maybe its not possible.

```py
def _findIdent(self) -> str:
    origCur = self.cursor
    while self.cursor < len(self.source):
        t = self.source[self.cursor]
        if ( # me trying to write python and still putting parents for no reason :)
            not t.isspace()
            and t not in "()"
        ):
            self.cursor += 1
        else:
            break
    return self.source[origCur : self.cursor]
```

the method you see above is probably the most interesting of them all and its used to find an identifier for other functions a.k.a its a helper function. This method checks if the character is not a space character and if its not any kind of syntax token meaning parents and spits out the token that it has found in the process consuming the token from the stream.

## Conclusion

The lexer/scanner is an important construct to being able to programatically go to trough text. The lexer produces a stream of predefined types of tokens to signify the structure of text.
In this laboratory work its elaborated a simple lexer for the programming language Scheme Lisp [1]. And learned what a lexer/scanner is.

## References:

[1] [Scheme Language](https://en.wikipedia.org/wiki/Scheme_(programming_language))
