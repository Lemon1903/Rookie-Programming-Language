import os
import re
import sys

from prettytable import PrettyTable

import constants

cursor = 0
current_indentation = 0
line_number = 0


# Token Classification
def classify_token(lexeme):
    if lexeme in constants.KEYWORDS:
        return "KEYWORD"
    if lexeme in constants.BOOLEAN_LITERAL:
        return "BOOLEAN_LITERAL"
    if lexeme in constants.LOGICAL_OPERATORS:
        return constants.LOGICAL_OPERATORS[lexeme]
    if lexeme in constants.OPERATORS:
        return constants.OPERATORS[lexeme]
    if lexeme in constants.DELIMITERS:
        return constants.DELIMITERS[lexeme]
    return "IDENTIFIER"


def advance_cursor():
    global cursor
    cursor += 1


# Generates single tokens of each line
def generate_token(line: str):
    global cursor
    lexeme = ""
    current_state = 0

    def update_lexeme(current_char):
        global cursor
        nonlocal lexeme
        cursor += 1
        lexeme += current_char

    while True:
        current_char = line[cursor] if cursor < len(line) else ""
        # initial state
        if current_state == 0:
            update_lexeme(current_char)
            if current_char in constants.DELIMITERS:
                return (classify_token(lexeme), lexeme)
            if current_char in constants.ALPHABET:
                current_state = 1
            elif current_char in constants.DIGITS:
                current_state = 3
            elif current_char in constants.OPERATORS:
                current_state = 5
            elif current_char == "!":
                current_state = 7
            elif current_char == '"':
                current_state = 8
            else:
                raise Exception(f"Invalid lexeme: \033[44m{lexeme}\033[49m")
        # identifier, keyword, and boolean literals
        elif current_state == 1:
            if current_char in constants.ALPHABET + constants.DIGITS:
                update_lexeme(current_char)
            elif current_char == "_":
                current_state = 2
            else:
                return (classify_token(lexeme), lexeme)
        # identifier with underscore
        elif current_state == 2:
            if current_char == "_":
                update_lexeme(current_char)
            elif current_char in constants.ALPHABET + constants.DIGITS:
                current_state = 1
            else:
                raise Exception(f"Invalid lexeme: {lexeme}")
        # number
        elif current_state == 3:
            if current_char in constants.DIGITS:
                update_lexeme(current_char)
            elif current_char == ".":
                current_state = 4
                update_lexeme(current_char)
            else:
                return ("FLOAT" if "." in lexeme else "NUMBER", lexeme)
        # float number
        elif current_state == 4:
            if current_char in constants.DIGITS:
                current_state = 3
                update_lexeme(current_char)
            else:
                raise Exception(f"Invalid lexeme: {lexeme + current_char}")
        # single operators (+ - * / % > < =)
        elif current_state in [5, 7]:
            if current_char == "=":
                current_state = 6
                update_lexeme(current_char)
            else:
                # not equal (!=)
                if current_state == 7:
                    raise Exception(f"Invalid lexeme: {lexeme + current_char}")
                return (classify_token(lexeme), lexeme)
        # double operators (+= -= *= /= >= <= ==)
        elif current_state == 6:
            if current_char == "=":
                raise Exception(f"Invalid lexeme: {lexeme + current_char}")
            else:
                return (classify_token(lexeme), lexeme)
        # string
        elif current_state == 8:
            update_lexeme(current_char)
            if current_char == '"':
                return ("STRING", lexeme)
            elif current_char == "":
                raise Exception(f"String was not closed: {lexeme}")


# Gets indentation of current line
def analyze_indentation(code_line: str):
    global cursor
    indentation = 0

    # count leading whitespaces or tabs
    for char in code_line:
        if char not in constants.SPACES:
            break
        cursor += 1
        indentation += constants.SPACES[char]

    # check if indentation is a multiple of specified indent size
    if indentation % constants.INDENT_SIZE != 0:
        raise IndentationError(f"Invalid indentation at line {line_number}")

    return indentation


def get_line_tokens(code_line: str):
    global cursor, current_indentation
    cursor = 0
    tokens = []

    # compare indentation with the previous line
    indentation = analyze_indentation(code_line)
    if indentation > current_indentation:
        tokens.append(("INDENT", None))
        current_indentation = indentation
    elif indentation < current_indentation:
        while indentation < current_indentation:
            tokens.append(("DEDENT", None))
            current_indentation -= constants.INDENT_SIZE

    # generate tokens for the current line
    while cursor < len(code_line):
        tokens.append(generate_token(code_line))
        while cursor < len(code_line) and code_line[cursor] in constants.SPACES:
            cursor += 1

    return tokens


# Input preprocessing
def preprocess_input(text):
    # removing single line comments
    text = re.sub(r"//.*", "", text)
    # removing multiline comments
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return text


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception("No file specified")

    filename = sys.argv[1]
    if not os.path.isfile(filename):
        raise FileNotFoundError("File not found")

    if not filename.endswith(".rook"):
        raise TypeError("File extension must end with .rook")

    with open(filename, "r") as file:
        code_lines = preprocess_input(file.read()).split("\n")

    all_tokens = []
    tokens_table = PrettyTable(["TOKEN", "LEXEME"])

    for line_no, line in enumerate(code_lines):
        line_number = line_no + 1
        # skip empty lines
        if line.strip():
            line_tokens = get_line_tokens(line)
            if line_number < len(code_lines):
                line_tokens.append(("NEWLINE", None))

            all_tokens += line_tokens
            tokens_table.add_rows(line_tokens)

    # write tokens to file
    with open("table.txt", "w") as file:
        file.write(tokens_table.get_string())

    print(tokens_table)
