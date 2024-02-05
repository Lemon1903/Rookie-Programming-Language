from token_stream import TokenStream


class Parser:
    def __init__(self, tokens: TokenStream):
        self.tokens = tokens
        self.current_token = None

    # ================ HELPER METHODS ================
    def match(self, type: str, to_match: str | list[str]):
        if type not in ["token", "lexeme"]:
            raise Exception("Invalid type")

        if self.tokens.is_empty():
            return False

        top_token = self.tokens.peek()
        lexeme = top_token[1] if top_token else None

        if isinstance(to_match, list):
            return (self.current_token if type == "token" else lexeme) in to_match
        return (self.current_token if type == "token" else lexeme) == to_match

    def consume(self, token):
        if self.match("token", token):
            self.tokens.advance()
            next_token = self.tokens.peek()
            self.current_token = next_token[0] if next_token else None
            return True
        return False

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
                raise Exception("Expected 'in' keyword after 'not' keyword")
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
        if self.match("token", ["NUMBER", "FLOAT", "STRING", "BOOLEAN_LITERAL"]):
            self.consume(self.current_token)
        # array
        elif self.match("token", "LBRACKET"):
            self.array()
        # expression
        elif self.consume("LPAREN"):
            self.expression()
            if not self.consume("RPAREN"):
                raise Exception("Expected closing parenthesis ')'")
        else:
            raise Exception("Invalid value")

    def array(self):
        self.consume("LBRACKET")

        # creation of array using 'to' keyword
        if self.consume("NUMBER"):
            if self.match("lexeme", "to") and not self.consume("KEYWORD"):
                raise Exception("Expected 'to' keyword")
            if not self.consume("NUMBER"):
                raise Exception("Expected integer after 'to' keyword")
            # check if there is an additional step keyword
            if self.match("lexeme", "step") and self.consume("KEYWORD"):
                if not self.consume("COLON"):
                    raise Exception("Expected colon ':'")
                if not self.consume("NUMBER"):
                    raise Exception("Expected integer after 'step' keyword")

        # get all values in array
        array_values = []
        while not self.match("token", "RBRACKET"):
            array_values.append(self.value())
            if not self.consume("COMMA"):
                break

        if not self.consume("RBRACKET"):
            raise Exception("Expected closing bracket ']'")

        return array_values

    # -- Expression End --

    def inst_block(self):
        if not self.consume("NEWLINE"):
            raise Exception("Expected newline")

        if not self.consume("INDENT"):
            raise Exception("Expected indentation")

        while self.match("lexeme", "instance") and self.consume("KEYWORD"):
            # consume optional relational operator
            if self.match("lexeme", ["<", ">", "==", "!=", ">=", "<="]):
                self.consume(self.current_token)

            # comparison part
            if not self.consume("IDENTIFIER") or self.consume("STRING"):
                raise Exception("Only accepts identifier or string")

            if not self.consume("COLON"):
                raise Exception("Expected colon ':'")
            self.block()

        if not self.consume("DEDENT"):
            raise Exception("Expected dedent")

    def block(self):
        if not self.consume("NEWLINE"):
            raise Exception("Expected newline")

        if not self.consume("INDENT"):
            raise Exception("Expected indentation")

        # run all statements in block
        while not self.tokens.is_empty() or not self.match("token", ["DEDENT", "EOF"]):
            self.statement()

        if not self.consume("DEDENT"):
            raise Exception("Expected dedent")

    # ---- Simple Statement ----

    def declaration_statement(self):
        # optional zero or more identifiers
        while self.match(",", "COMMA"):
            if not self.consume("IDENTIFIER"):
                raise Exception("Expected identifier")

        if not self.consume("ASSIGN"):
            raise Exception("Expected assignment '='")
        self.expression()

        # optional zero or more expressions
        while self.consume("COMMA"):
            self.expression()

    def assign_statement(self):
        self.consume(self.current_token)
        self.expression()

    def input_statement(self):
        # consume 'input' keyword
        self.consume("KEYWORD")
        if not self.consume("LPAREN"):
            raise Exception("Expected '(' after 'input'")

        self.consume("STRING")
        if not self.consume("RPAREN"):
            raise Exception("Expected ')' after arguments")

    def output_statement(self):
        # consume 'print' keyword
        self.consume("BUILT_IN_FUNCTION")
        if not self.consume("LPAREN"):
            raise Exception("Expected '(' after 'print'")

        # optional expressions
        while not self.match("token", ["RPAREN", "KEYWORD"]):
            self.expression()
            if not self.consume("COMMA"):
                break

        # optional separator argument
        if self.match("lexeme", "separator"):
            if not self.consume("ASSIGN"):
                raise Exception("Error: Argument 'separator' is not defined")
            if not self.consume("STRING"):
                raise Exception("Expected an argument string value")

        if not self.consume("RPAREN"):
            raise Exception("Expected ')' after expressions and arguments")

    def simple_stmt(self):
        if self.match("lexeme", "print"):
            self.output_statement()
        self.consume("IDENTIFIER")

        # declaration statement
        if self.match("token", "COMMA") or self.match("token", "ASSIGN"):
            self.declaration_statement()
        # input statement
        elif self.consume("ASSIGN") and self.match("lexeme", "input"):
            self.input_statement()
        # assignment statement
        elif self.match("lexeme", "=, +=, -=, *=, /="):
            self.assign_statement()
        else:
            raise Exception("Invalid statement")

    # ---- Simple Statement End ----

    # ---- Compound Statement ----

    def if_statement(self):
        self.consume("KEYWORD")
        self.expression()

        if not self.consume("COLON"):
            raise Exception("Expected colon ':'z")
        self.block()

        # optional zero or more elif statements
        while self.match("lexeme", "elif"):
            self.consume("KEYWORD")
            self.expression()

            if not self.consume("COLON"):
                raise Exception("Expected colon ':'")
            self.block()

        # optional else statement
        if self.match("lexeme", "else"):
            self.consume("KEYWORD")

            if not self.consume("COLON"):
                raise Exception("Expected colon ':'")
            self.block()

    def which_statement(self):
        self.consume("KEYWORD")
        if not self.consume("IDENTIFIER"):
            raise Exception("Expected identifier")

        if not self.consume("COLON"):
            raise Exception("Expected colon ':'")
        self.inst_block()

    def while_statement(self):
        self.consume("KEYWORD")
        self.expression()
        if not self.consume("COLON"):
            raise Exception("Expected colon ':'")
        self.block()

    def for_statement(self):
        self.consume("KEYWORD")
        if not self.consume("IDENTIFIER"):
            raise Exception("Expected identifier")

        # optional another identifier
        if self.consume("COMMA") and not self.consume("IDENTIFIER"):
            raise Exception("Expected identifier")

        if not self.consume("KEYWORD"):
            raise Exception("Expected keyword 'in'")

        if not self.consume("COLON"):
            raise Exception("Expected colon ':'")
        self.block()

    def function_statement(self):
        self.consume("KEYWORD")
        if not self.consume("IDENTIFIER"):
            raise Exception("Expected identifier")

        if not self.consume("LPAREN"):
            raise Exception("Expected opening parenthesis '('")

        # optional zero or more parameters
        while not self.match("token", "RPAREN"):
            if not self.consume("IDENTIFIER"):
                raise Exception("Expected identifier")
            if self.consume("ASSIGN"):
                self.expression()
            if not self.consume("COMMA"):
                break

        if not self.consume("RPAREN"):
            raise Exception("Expected closing parenthesis ')'")

        if not self.consume("COLON"):
            raise Exception("Expected colon ':'")
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
        # compound stmt
        elif self.match("token", "KEYWORD"):
            self.compound_stmt()

        # syntax error
        if not self.consume("NEWLIUNE"):
            raise Exception("Expected newline at the end of the statement")

        return True

    def rook_pl(self):
        statements_passed = 0
        while not self.tokens.is_empty() or not self.consume("EOF"):
            self.statement()
            statements_passed += 1
        return statements_passed

    def parse(self):
        print(self.rook_pl())
        if self.tokens.is_empty():
            print("Parsing successful")
