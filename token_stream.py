from typing import List, Tuple


class TokenStream:
    def __init__(self):
        self.tokens: List[Tuple[str, str]] = []

    # checks if the list is empty
    def is_empty(self):
        return len(self.tokens) == 0

    # returns the first token
    def peek(self):
        if self.tokens:
            return self.tokens[0]

    # adds a token to the end of the list
    def add(self, token: Tuple[str, str]):
        self.tokens.append(token)

    # removes the first token
    def remove(self):
        if len(self.tokens) < 1:
            return None
        return self.tokens.pop(0)

    # displays the tokens
    def display(self):
        print(self.tokens)
