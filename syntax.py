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

        # success = False
        # valid_ops = ["+", "-", "*", "/", "%", '<', '>', '==', '!=', '>=', '<=']

        # self.value()
        # while self.match("lexeme", valid_ops):
        #     success = True
        #     self.consume("OPERATORS")
        #     self.value()

        # if not success:
        #     raise Exception("Invalid arithmetic operator used")

    def and_test(self):
        self.not_test()
        while self.match("lexeme", "and"):
            self.consume("KEYWORD")
            self.not_test()

    def not_test(self):
        if not self.match("lexeme", "not"):
            self.comparison()

    def comparison(self):
        pass

    def expr(self):
        pass

    def factor(self):
        pass

    def term(self):
        pass

    def value(self):
        # array
        if self.match("token", "LBRACKET"):
            self.array()
        # expression
        elif self.consume("LPAREN"):
            expression = self.expression()
            if not self.consume("RPAREN"):
                raise Exception("Expected closing parenthesis ')'")
            return expression

        # number, identifier, string, bool_literal
        return self.consume(self.current_token)

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
                self.consume("OPERATORS")

            self.value()
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
        while self.statement():
            pass

        if not self.consume("DEDENT"):
            raise Exception("Expected dedent")

    def condition(self):
        self.value()
        if self.match("lexeme", ["<", ">", "==", "!=", ">=", "<="]):
            self.consume("OPERATORS")
            self.value()

    def simple_stmt(self):
        pass

    def if_statement(self):
        if not self.consume("KEYWORD"):
            raise Exception("Expected keyword 'if'")
        self.condition()

        if not self.consume("COLON"):
            raise Exception("Expected colon ':'")
        self.block()

    def which_statement(self):
        if not self.consume("KEYWORD"):
            raise Exception("Expected keyword 'which'")

        if not self.consume("IDENTIFIER"):
            raise Exception("Expected identifier")

        if not self.consume("COLON"):
            raise Exception("Expected colon ':'")
        self.inst_block()

    def while_statement(self):
        if not self.consume("KEYWORD"):
            raise Exception("Expected keyword 'while'")
        self.condition()

        if not self.consume("COLON"):
            raise Exception("Expected colon ':'")
        self.block()

    def for_statement(self):
        if not self.consume("KEYWORD"):
            raise Exception("Expected keyword 'for'")

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

    def compound_stmt(self):
        if self.match("lexeme", "if"):
            self.if_statement()
        elif self.match("lexeme", "which"):
            self.which_statement()
        elif self.match("lexeme", "while"):
            self.while_statement()
        elif self.match("lexeme", "for"):
            self.for_statement()

    def statement(self):
        # simple stmt
        if self.match("token", ["IDENTIFIER", "BUILT_IN_FUNCTION"]):
            self.simple_stmt()
        # compound stmt
        elif self.match("token", "KEYWORD"):
            self.compound_stmt()

        # syntax error
        if not self.consume("NEWLIUNE"):
            raise Exception("Expected newline")

        return True

    def rook_pl(self):
        statements_passed = 0
        while self.statement():
            statements_passed += 1
        return statements_passed

    def parse(self):
        print(self.rook_pl())
        if self.tokens.is_empty():
            print("Parsing successful")
