import os
import re

from prettytable import PrettyTable

import constants


class Lexer:
    def __init__(self, filepath: str):
        self._filename = os.path.basename(filepath).split(".")[0]
        self._cursor = 0
        self._lexeme = ""
        self._tokens = []
        self._current_state = 0
        self._current_indentation = 0

        with open(filepath, "r") as file:
            self._code_lines = self.preprocess_input(file.read())

    def start_parse(self):
        for line_number, line in enumerate(self._code_lines):
            self._line_number = line_number + 1
            if line.strip():  # skip empty lines
                self.get_line_tokens(line)

    # Input preprocessing
    def preprocess_input(self, code: str):
        # removing single line comments
        code = re.sub(r"//.*", "", code)
        # removing multiline comments
        code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
        # splitting code into multiple lines
        return code.split("\n")

    def get_line_tokens(self, line: str):
        self._cursor = 0

        # compare indentation with the previous line
        indentation = self.analyze_indentation(line)
        if indentation > self._current_indentation:
            self._tokens.append(("INDENT", ""))
            self._current_indentation = indentation
        elif indentation < self._current_indentation:
            # Generate DEDENT tokens for each level decreased
            while indentation < self._current_indentation:
                self._tokens.append(("DEDENT", ""))
                self._current_indentation -= constants.INDENT_SIZE

        self.generate_tokens(line)

    # Gets indentation of current line
    def analyze_indentation(self, line: str):
        indentation = 0

        # count leading whitespaces or tabs
        for char in line:
            if char not in constants.SPACES:
                break
            self._cursor += 1
            indentation += constants.SPACES[char]

        # check if indentation is a multiple of specified indent size
        if indentation % constants.INDENT_SIZE != 0:
            raise IndentationError(f"Invalid indentation at line {self._line_number}")

        return indentation

    # Generate tokens for the current line
    def generate_tokens(self, line: str):
        while self._cursor < len(line):
            current_char = line[self._cursor]
            # initial state
            if self._current_state == 0:
                # skip whitespaces
                if current_char in constants.SPACES:
                    self._cursor += 1
                    continue

                self.update_lexeme(current_char)
                if current_char in constants.DELIMITERS:
                    self.add_token()
                elif current_char in constants.ALPHABET:
                    self._current_state = 1
                elif current_char in constants.DIGITS:
                    self._current_state = 3
                elif current_char in constants.OPERATORS:
                    self._current_state = 5
                elif current_char == "!":
                    self._current_state = 7
                elif current_char == '"':
                    self._current_state = 8
                else:
                    raise Exception(f"Invalid lexeme: {self._lexeme}")
            # identifier, keyword, and boolean literals
            elif self._current_state == 1:
                if current_char in constants.ALPHABET + constants.DIGITS:
                    self.update_lexeme(current_char)
                elif current_char == "_":
                    self._current_state = 2
                else:
                    self.add_token()
            # identifier with underscore
            elif self._current_state == 2:
                if current_char == "_":
                    self.update_lexeme(current_char)
                elif current_char in constants.ALPHABET + constants.DIGITS:
                    self._current_state = 1
                else:
                    raise Exception(f"Invalid lexeme: {self._lexeme + current_char}")
            # number
            elif self._current_state == 3:
                if current_char in constants.ALPHABET:
                    raise Exception(f"Invalid lexeme: {self._lexeme + current_char}")

                if current_char in constants.DIGITS:
                    self.update_lexeme(current_char)
                elif current_char == ".":
                    self._current_state = 4
                    self.update_lexeme(current_char)
                else:
                    self.add_token()
            # float number
            elif self._current_state == 4:
                if current_char in constants.DIGITS:
                    self._current_state = 3
                else:
                    raise Exception(f"Invalid lexeme: {self._lexeme + current_char}")
            # single operators (+ - * / % > < =)
            elif self._current_state in [5, 7]:
                if current_char == "=":
                    self._current_state = 6
                    self.update_lexeme(current_char)
                else:
                    # invalid double operators (-+, ++, =+, --) and not equal (!=)
                    if current_char in constants.OPERATORS or self._current_state == 7:
                        raise Exception(f"Invalid lexeme: {self._lexeme + current_char}")
                    self.add_token()
            # double operators (+= -= *= /= >= <= ==)
            elif self._current_state == 6:
                if current_char == "=":
                    raise Exception(f"Invalid lexeme: {self._lexeme + current_char}")
                else:
                    self.add_token()
            # string
            elif self._current_state == 8:
                self.update_lexeme(current_char)
                if current_char == '"':  # closing quote
                    self.add_token()

        # checks if string is closed
        if self._current_state == 8:
            raise Exception(f"String was not closed: {self._lexeme}")

        self.add_token()

    def update_lexeme(self, current_char):
        self._cursor += 1
        self._lexeme += current_char

    def add_token(self):
        self._tokens.append(self.classify_token())
        self._lexeme = ""
        self._current_state = 0

    def classify_token(self):
        token_name = "IDENTIFIER"
        if self._lexeme in constants.KEYWORDS:
            token_name = "KEYWORD"
        elif self._lexeme in constants.BOOLEAN_LITERAL:
            token_name = "BOOLEAN_LITERAL"
        elif self._lexeme in constants.LOGICAL_OPERATORS:
            token_name = constants.LOGICAL_OPERATORS[self._lexeme]
        elif self._lexeme in constants.OPERATORS:
            token_name = constants.OPERATORS[self._lexeme]
        elif self._lexeme in constants.DELIMITERS:
            token_name = constants.DELIMITERS[self._lexeme]
        elif self._lexeme in constants.BUILT_IN_FUNCTIONS:
            token_name = "BUILT_IN_FUNCTION"
        elif self._lexeme == "":
            token_name = "NEWLINE" if self._line_number < len(self._code_lines) else "EOF"
        elif self._current_state == 3:
            token_name = "FLOAT" if "." in self._lexeme else "NUMBER"
        elif self._current_state == 8:
            token_name = "STRING"
        return (token_name, self._lexeme)

    def output_table(self):
        # print tokens to console
        tokens_table = PrettyTable(["TOKEN", "LEXEME"])
        tokens_table.add_rows(self._tokens)
        print(tokens_table)

        # write tokens to file
        output_path = os.path.join("rookie-tables", f"{self._filename}.rtable")
        with open(output_path, "w") as file:
            file.write(tokens_table.get_string())
