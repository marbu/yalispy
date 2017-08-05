#!/usr/bin/env python3
# -*- coding: utf8 -*-


import argparse
import math
import operator as op


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


#
# Environment
#


class Procedure(object):
    """
    A user-defined Scheme procedure.
    """

    def __init__(self, params, body, env):
        self.params = params
        self.body = body
        self.env = env

    def __call__(self, *args):
        return eval(self.body, Env(self.params, args, self.env))


class Env(dict):
    """
    An environment: a dict of {'val': val} pairs, with an outer Env.
    """

    def __init__(self, params=(), args=(), outer=None):
        self.update(zip(params, args))
        self.outer = outer

    def find(self, var):
        """
        Find the innermost Env where var appears.
        """
        return self if (var in self) else self.outer.find(var)


def standard_env():
    """
    An environment with some Scheme standard procedures.
    """
    env = Env()
    env.update(vars(math))
    env.update({
        '+':       op.add,
        '-':       op.sub,
        '*':       op.mul,
        '/':       op.truediv,
        '>':       op.gt,
        '<':       op.lt,
        '>=':      op.ge,
        '<=':      op.le,
        '=':       op.eq,
        'abs':     abs,
        'append':  op.add,
        'apply':   lambda f, x: f(*x),
        'begin':   lambda *x: x[-1],
        'car':     lambda x: x[0],
        'cdr':     lambda x: x[1:],
        'cons':    lambda x, y: [x] + y,
        'eq?':     op.is_,
        'equal?':  op.eq,
        'length':  len,
        'list':    lambda *x: list(x),
        'list?':   lambda x: isinstance(x, list),
        'map':     lambda x, y: list(map(x, y)),
        'max':     max,
        'min':     min,
        'not':     op.not_,
        'null?':   lambda x: x == [],
        'number?': lambda x: isinstance(x, Number),
        'procedure?': callable,
        'round':   round,
        'symbol?': lambda x: isinstance(x, Symbol),
        'display': lambda x: print(schemestr(x), end=''),
        'newline': lambda: print(),
        })
    return env


GLOBAL_ENV = standard_env()


#
# Evaluation
#


def eval(x, env=GLOBAL_ENV):
    """
    Evaluate an expression in an environment.
    """
    # variable reference
    if isinstance(x, Symbol):
        return env.find(x)[x]
    # constant literal
    elif not isinstance(x, List):
        return x
    # quotation
    elif x[0] == 'quote':
        (_, exp) = x
        return exp
    # conditional
    elif x[0] == "if":
        (_, test, conseq, alt) = x
        exp = (conseq if eval(test, env) else alt)
        return eval(exp, env)
    # definition
    elif x[0] == "define":
        (_, var, exp) = x
        env[var] = eval(exp, env)
    # assignment
    elif x[0] == "set!":
        (_, var, exp) = x
        env.find(var)[var] = eval(exp, env)
    # procedure
    elif x[0] == "lambda":
        (_, params, body) = x
        return Procedure(params, body, env)
    # procedure call
    else:
        proc = eval(x[0], env)
        args = [eval(arg, env) for arg in x[1:]]
        return proc(*args)

#
# REPL
#

def repl(prompt='lis.py> '):
    while True:
        val = eval(parse(input(prompt)))
        if val is not None:
            print(schemestr(val))


def schemestr(exp):
    """
    Convert a Python object back into a Scheme-readable string.
    """
    if isinstance(exp, List):
        return "(" + " ".join(map(schemestr, exp)) + ")"
    else:
        return str(exp)


#
# main
#

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description="Yet Another lispy clone.")
    ap.add_argument("source", nargs='?', help="lispy source code file")
    args = ap.parse_args()

    if args.source is None:
        try:
            repl()
        except EOFError:
            print()
    else:
        with open(args.source, "r") as source_file:
            source = source_file.read()
            eval(parse(source))
