import sys
from lexer import Lexer


def main():
    print([str(s) for s in Lexer(
        #Example
        """
        (define a 12)
        (define b 12)
        (+ a b)
        """).lex()])


if __name__ == "__main__":
    main()
