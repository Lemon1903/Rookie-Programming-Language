from token_stream import TokenStream


class Parser:
    def __init__(self, tokens: TokenStream):
        self.tokens = tokens
        self.current_token = self.tokens.peek()

    def consume(self, token):
        if not self.tokens.is_empty() and self.current_token and self.current_token[0] == token:
            self.tokens.remove()
            self.current_token = self.tokens.peek()
            return True
        return False

    def value(self):
        pass

    def condition(self):
        pass

    def block(self):
        if not self.consume("NEWLINE"):
            raise Exception("Expected newline")

        if not self.consume("INDENT"):
            raise Exception("Expected indentation")

        while self.statement():
            pass

        if not self.consume("DEDENT"):
            raise Exception("Expected dedent")

    def if_statement(self):
        # consume "if"
        if not self.consume("KEYWORD"):
            raise Exception("Expected keyword 'if'")
        self.condition()

        if not self.consume("COLON"):
            raise Exception("Expected colon ':'")
        self.block()

    def which_statement(self):
        pass

    def while_statement(self):
        pass

    def for_statement(self):
        pass

    def compound_stmt(self):
        current_lexeme = self.current_token[1] if self.current_token else None
        if current_lexeme == "if":
            self.if_statement()
        elif current_lexeme == "which":
            self.which_statement()
        elif current_lexeme == "while":
            self.while_statement()
        elif current_lexeme == "for":
            self.for_statement()

    def statement(self):
        current_token = self.current_token[0] if self.current_token else None

        # simple stmt
        if current_token in ["IDENTIFIER", "BUILT_IN_FUNCTION"]:
            pass
        # compound stmt
        elif current_token == "KEYWORD":
            self.compound_stmt()

        # syntax error
        if not self.consume("NEWLIUNE"):
            raise Exception("Expected newline")

        return True

    def rook_pl(self):
        statements_passed = 0
        while True:
            if not self.statement():
                break
            statements_passed += 1
        return statements_passed

    def parse(self):
        print(self.rook_pl())
        if self.tokens.is_empty():
            print("Parsing successful")
