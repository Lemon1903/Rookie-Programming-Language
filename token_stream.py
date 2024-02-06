from typing import List

from token_ import Token


class TokenStream:
    def __init__(self):
        self._tokens: List[Token] = []

    def get_tokens(self):
        return self._tokens

    # checks if the list is empty
    def is_empty(self):
        return len(self._tokens) == 0

    # returns the first token
    def peek(self):
        if self._tokens:
            return self._tokens[0]
        else:
            raise Exception("Cannot peek to an empty queue")

    # adds a token to the end of the list
    def add(self, token: Token):
        self._tokens.append(token)

    # removes the first token from the list
    def advance(self):
        if len(self._tokens) > 0:
            return self._tokens.pop(0)
