INDENT_SIZE = 4
DIGITS = list("0123456789")
ALPHABET = list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
SPACES = {" ": 1, "\t": INDENT_SIZE}
OPERATORS = {
    "+": "PLUS",
    "-": "MINUS",
    "*": "MULTIPLY",
    "/": "DIVIDE",
    "%": "MODULO",
    ">": "GREATER",
    "<": "LESS",
    "=": "ASSIGN",
    ">=": "GREATEROREQUAL",
    "<=": "LESSOREQUAL",
    "==": "EQUAL",
    "!=": "NOTEQUAL",
    "+=": "PLUSASSIGN",
    "-=": "MINUSASSIGN",
    "*=": "MULTIPLYASSIGN",
    "/=": "DIVIDEASSIGN",
}
LOGICAL_OPERATORS = {
    "and": "AND",
    "or": "OR",
    "not": "NOT",
}
DELIMITERS = {
    ".": "DOT",
    ",": "COMMA",
    ":": "COLON",
    "(": "LPAREN",
    ")": "RPAREN",
    "[": "LBRACKET",
    "]": "RBRACKET",
}
KEYWORDS = [
    "for",
    "while",
    "break",
    "continue",
    "in",
    "define",
    "return",
    "if",
    "elif",
    "else",
    "pass",
    "import",
    "from",
    "to",
    "step",
    "which",
    "instance",
    "default",
    "separator",
]
BOOLEAN_LITERAL = ["true", "false"]
BUILT_IN_FUNCTIONS = ["print", "input"]
