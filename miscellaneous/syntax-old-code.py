from token_stream import TokenStream


class ASTNode:
    def __init__(self, node_type: str | None, children=None):
        self.node_type = node_type
        self.children = children if children else []

    def add_child(self, child):
        self.children.append(child)

    def add_children(self, children: list):
        for child in children:
            self.children.append(child)


class Parser:
    def __init__(self, tokens: TokenStream):
        self.tokens = tokens
        self.current_token = self.tokens.peek()

    def consume(self, token):
        current_token = self.current_token[0] if self.current_token else None
        if not self.tokens.is_empty() and current_token == token:
            self.tokens.advance()
            self.current_token = self.tokens.peek()
            return True
        return False

    def expr(self):
        pass

    def array(self):
        self.consume("LBRACKET")

        # creation of array using 'to' keyword
        # if self.consume("NUMBER"):

        # get all values in array
        array_values = []
        while not self.consume("RBRACKET"):
            array_values.append(self.value())
            if not self.consume("COMMA"):
                break

        if not self.consume("RBRACKET"):
            raise Exception("Expected closing bracket ']'")

        return ASTNode("ARRAY", array_values)

    def value(self):
        current_token = self.current_token[0] if self.current_token else None
        current_lexeme = self.current_token[1] if self.current_token else None

        # array
        if self.current_token == "LBRACKET":
            self.array()
        # expression
        elif self.consume("LPAREN"):
            expr = self.expr()
            self.consume("RPAREN")
            return expr

        self.consume(current_token)
        return ASTNode("VALUE", [ASTNode(current_token, [current_lexeme])])

    def condition(self):
        pass

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

    def if_statement(self):
        self.consume("KEYWORD")
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
