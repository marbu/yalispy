#!/usr/bin/env python3
# -*- coding: utf8 -*-

#
# Representation of Scheme objects
#

Symbol = str          # A Scheme Symbol is implemented as a Python str
List   = list         # A Scheme List is implemented as a Python list
Number = (int, float) # A Scheme Number is implemented as a Python int or float

#
# Parsing
#

def parse(program):
    """
    Read a Scheme expression from a string to create AST (list).
    """
    return read_from_tokens(tokenize(program))


def tokenize(chars):
    """
    Convert a string of characters into a list of tokens.
    """
    return chars.replace("(", " ( ").replace(")", " ) ").split()


def read_from_tokens(tokens):
    """
    Read an expression from a list of tokens to create AST.
    """
    if len(tokens) == 0:
        raise SyntaxError("unexpected EOF while reading")
    token = tokens.pop(0)
    if "(" == token:
        ast_list = []
        while tokens[0] != ")":
            ast_list.append(read_from_tokens(tokens))
        tokens.pop(0)  # pop off ")"
        return ast_list
    elif ")" == token:
        raise SyntaxError("unexpected ')'")
    else:
        return atom(token)


def atom(token):
    """
    Numbers become numbers; every other token is a symbol.
    """
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return Symbol(token)
