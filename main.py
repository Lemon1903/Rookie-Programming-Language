import os
import sys

from lexer import Lexer
from syntax import Parser

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception("No file specified")

    filepath = sys.argv[1]
    if not os.path.isfile(filepath):
        raise FileNotFoundError("File not found")

    if not filepath.endswith(".rook"):
        raise TypeError("File extension must end with .rook")

    lexer = Lexer(filepath)
    lexer.start_parse()
    lexer.output_table()

    parser = Parser(lexer.get_tokens())
    parser.parse()
