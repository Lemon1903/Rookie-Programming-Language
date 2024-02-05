from typing import List, Tuple


class TokenStream:
    def __init__(self):
        self._tokens: List[Tuple[str, str]] = []

    def get_tokens(self):
        return self._tokens

    # checks if the list is empty
    def is_empty(self):
        return len(self._tokens) == 0

    # returns the first token
    def peek(self):
        if self._tokens:
            return self._tokens[0]

    # adds a token to the end of the list
    def add(self, token: Tuple[str, str]):
        self._tokens.append(token)

    # removes the first token from the list
    def advance(self):
        if len(self._tokens) < 1:
            return None
        return self._tokens.pop(0)
