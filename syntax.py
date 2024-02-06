import os

from token_stream import TokenStream


class Parser:
    def __init__(self, tokens: TokenStream):
        self.tokens = tokens
        self.previous_token = None
        self.advance(False)

    # ================ HELPER METHODS ================
    def match(self, type: str, to_match: str | list[str]):
        if type not in ["token", "lexeme"]:
            raise Exception("Invalid type")

        if self.tokens.is_empty():
            return False

        if isinstance(to_match, list):
            return (self.current_token if type == "token" else self.current_lexeme) in to_match
        return (self.current_token if type == "token" else self.current_lexeme) == to_match

    def consume(self, token):
        if self.match("token", token):
            self.advance()
            return True
        return False

    def advance(self, do_advance: bool = True):
        if do_advance:
            self.previous_token = self.tokens.advance()
        if not self.tokens.is_empty():
            next_token = self.tokens.peek()
            self.current_token = next_token.name
            self.current_lexeme = next_token.lexeme

    def print_error(self, message: str):
        token = self.tokens.peek()
        print(f"Error at line {token.line_no}: {message}\n{token.line_code}")
        print(" " * (token.column_no - token.indent_level - len(token.lexeme) + 2) + "^" * len(token.lexeme))
        os._exit(1)

    # ================ PARSER METHODS ================
    # ---- Expression ----

    def expression(self):
        self.and_test()
        while self.match("lexeme", "and"):
            self.consume("KEYWORD")
            self.and_test()

    def and_test(self):
        self.not_test()
        if self.match("lexeme", "and") and self.consume("AND"):
            self.not_test()

    def not_test(self):
        self.consume("NOT")
        self.comparison()

    def comparison(self):
        comp_ops = ["<", ">", "==", "!=", ">=", "<=", "not", "in"]
        self.expr()
        while self.match("lexeme", comp_ops):
            if self.consume("NOT") and (not self.match("lexeme", "in") or not self.consume("KEYWORD")):
                self.print_error("Expected 'in' keyword after 'not' keyword")
            else:
                self.consume("KEYWORD" if self.match("lexeme", "in") else self.current_token)
            self.expr()

    def expr(self):
        self.factor()
        while self.match("lexeme", ["+", "-"]):
            self.consume(self.current_token)
            self.factor()

    def factor(self):
        self.term()
        while self.match("lexeme", ["*", "/", "%"]):
            self.consume(self.current_token)
            self.term()

    def term(self):
        self.consume("UNARY")
        self.value()

    def value(self):
        if self.match("token", ["IDENTIFIER", "NUMBER", "FLOAT", "STRING", "BOOLEAN_LITERAL"]):
            self.consume(self.current_token)
        # array
        elif self.match("token", "LBRACKET"):
            self.array()
        # expression
        elif self.consume("LPAREN"):
            self.expression()
            if not self.consume("RPAREN"):
                self.print_error("Expected closing parenthesis ')'")
        else:
            self.print_error("Invalid value")

    def array(self):
        self.consume("LBRACKET")

        if self.consume("NUMBER"):
            self.consume("COMMA")

        # get all values in array
        while not self.match("token", "RBRACKET") and not self.match("lexeme", "to"):
            self.expression()
            if not self.consume("COMMA"):
                break

        # array instantiation using 'to' keyword
        if self.consume("KEYWORD"):
            if not self.consume("NUMBER"):
                self.print_error("Expected integer after 'to' keyword")
            # check if there is an additional step keyword
            if self.match("lexeme", "step") and self.consume("KEYWORD"):
                if not self.consume("COLON"):
                    self.print_error("Expected colon ':'")
                if not self.consume("NUMBER"):
                    self.print_error("Expected integer after 'step' keyword")

        if not self.consume("RBRACKET"):
            self.print_error("Expected closing bracket ']'")

    # -- Expression End --

    def ins_block(self):
        if not self.consume("NEWLINE"):
            self.print_error("Expected newline")

        if not self.consume("INDENT"):
            self.print_error("Expected indentation")

        # instance part
        while self.match("lexeme", "instance") and self.consume("KEYWORD"):
            # consume optional relational operator
            if self.match("lexeme", ["<", ">", "==", "!=", ">=", "<="]):
                self.consume(self.current_token)

            # comparison part
            if self.match("token", ["NUMBER", "STRING"]):
                self.consume(self.current_token)
            else:
                self.print_error("Expected number or string")

            if not self.consume("COLON"):
                self.print_error("Expected colon ':'")
            self.block()

        # default part
        if self.match("lexeme", "default"):
            self.consume("KEYWORD")
            if not self.consume("COLON"):
                self.print_error("Expected colon ':'")
            self.block()

        if not self.consume("DEDENT"):
            self.print_error("Expected dedent")

    def block(self):
        if not self.consume("NEWLINE"):
            self.print_error("Expected newline")

        if not self.consume("INDENT"):
            self.print_error("Expected indentation")

        # run all statements in block
        while not self.tokens.is_empty() and not self.match("token", "DEDENT"):
            self.statement()

        if not self.consume("DEDENT"):
            self.print_error("Expected dedent")

    # ---- Simple Statement ----

    def declaration_statement(self):
        # optional zero or more identifiers
        while self.match("token", "COMMA"):
            if not self.consume("IDENTIFIER"):
                self.print_error("Expected identifier")

        if not self.consume("ASSIGN"):
            self.print_error("Expected assignment '='")

        # input statement
        if self.match("lexeme", "input"):
            self.input_statement()
            return

        self.expression()

        # optional zero or more expressions
        while self.consume("COMMA"):
            self.expression()

    def assign_statement(self):
        self.consume(self.current_token)
        self.expression()

    def input_statement(self):
        # consume 'input' keyword
        self.consume("BUILT_IN_FUNCTION")
        if not self.consume("LPAREN"):
            self.print_error("Expected '(' after 'input'")

        if not self.match("token", "RPAREN") and not self.consume("STRING"):
            self.print_error("Expected string argument for 'input' function")

        if not self.consume("RPAREN"):
            self.print_error("Expected ')' after arguments")

    def output_statement(self):
        # consume 'print' keyword
        self.consume("BUILT_IN_FUNCTION")
        if not self.consume("LPAREN"):
            self.print_error("Expected '(' after 'print'")

        # optional expressions
        while not self.match("token", "RPAREN") and not self.match("lexeme", "separator"):
            self.expression()
            if not self.consume("COMMA"):
                break

        # optional separator argument
        if self.consume("KEYWORD"):
            if not self.consume("ASSIGN"):
                self.print_error("Argument 'separator' is not defined")
            if not self.consume("STRING"):
                self.print_error("Expected an argument string value")

        if not self.consume("RPAREN"):
            self.print_error("Expected ')' after expressions and arguments")

    def simple_stmt(self):
        if self.match("lexeme", "print"):
            self.output_statement()
            return

        self.consume("IDENTIFIER")

        # declaration statement
        if self.match("token", ["COMMA", "ASSIGN"]):
            self.declaration_statement()
        # assignment statement
        elif self.match("lexeme", ["+=", "-=", "*=", "/="]):
            self.assign_statement()
        else:
            self.print_error("Invalid statement")

    # ---- Simple Statement End ----

    # ---- Compound Statement ----

    def if_statement(self):
        self.consume("KEYWORD")
        self.expression()

        if not self.consume("COLON"):
            self.print_error("Expected colon ':'")
        self.block()

        # optional zero or more elif statements
        while self.match("lexeme", "elif"):
            self.consume("KEYWORD")
            self.expression()

            if not self.consume("COLON"):
                self.print_error("Expected colon ':'")
            self.block()

        # optional else statement
        if self.match("lexeme", "else"):
            self.consume("KEYWORD")

            if not self.consume("COLON"):
                self.print_error("Expected colon ':'")
            self.block()

    def which_statement(self):
        self.consume("KEYWORD")
        if not self.consume("IDENTIFIER"):
            self.print_error("Expected identifier")

        if not self.consume("COLON"):
            self.print_error("Expected colon ':'")
        self.ins_block()

    def while_statement(self):
        self.consume("KEYWORD")
        self.expression()
        if not self.consume("COLON"):
            self.print_error("Expected colon ':'")
        self.block()

    def for_statement(self):
        self.consume("KEYWORD")
        if not self.consume("IDENTIFIER"):
            self.print_error("Expected identifier")

        # optional another identifier
        if self.consume("COMMA") and not self.consume("IDENTIFIER"):
            self.print_error("Expected identifier")

        if not self.consume("KEYWORD"):
            self.print_error("Expected keyword 'in'")

        if self.match("token", "LBRACKET"):
            self.array()
        elif self.match("token", "IDENTIFIER"):
            self.consume("IDENTIFIER")
        else:
            self.print_error("Expected array or identifier")

        if not self.consume("COLON"):
            self.print_error("Expected colon ':'")
        self.block()

    def function_statement(self):
        self.consume("KEYWORD")
        if not self.consume("IDENTIFIER"):
            self.print_error("Expected identifier")

        if not self.consume("LPAREN"):
            self.print_error("Expected opening parenthesis '('")

        # optional zero or more parameters
        while not self.match("token", "RPAREN"):
            if not self.consume("IDENTIFIER"):
                self.print_error("Expected identifier")
            if self.consume("ASSIGN"):
                self.expression()
            if not self.consume("COMMA"):
                break

        if not self.consume("RPAREN"):
            self.print_error("Expected closing parenthesis ')'")

        if not self.consume("COLON"):
            self.print_error("Expected colon ':'")
        self.block()

    def compound_stmt(self):
        if self.match("lexeme", "if"):
            self.if_statement()
        elif self.match("lexeme", "which"):
            self.which_statement()
        elif self.match("lexeme", "while"):
            self.while_statement()
        elif self.match("lexeme", "for"):
            self.for_statement()
        elif self.match("lexeme", "define"):
            self.function_statement()

    # ---- Compound Statement End ----

    def statement(self):
        # simple stmt
        if self.match("token", ["IDENTIFIER", "BUILT_IN_FUNCTION"]):
            self.simple_stmt()
            if not self.consume("NEWLINE"):
                self.print_error("Expected newline at the end of the statement")

        # compound stmt
        elif self.match("token", "KEYWORD"):
            self.compound_stmt()

    def rook_pl(self):
        while not self.tokens.is_empty() and not self.consume("EOF"):
            self.statement()

    def parse(self):
        self.rook_pl()
        if self.tokens.is_empty():
            print("Parsing successful")
