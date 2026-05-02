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