class Token:
    def __init__(self, name: str, lexeme: str, line_no: int, line_code="", column_no=0, indent_level=0) -> None:
        self.name = name
        self.lexeme = lexeme
        self.line_no = line_no
        self.column_no = column_no
        self.line_code = "  " + line_code.strip()
        self.indent_level = indent_level
