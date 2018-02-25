#!/usr/bin/env python3
# -*- coding: utf8 -*-


import argparse
import io
import math
import operator as op
import re
import sys


#
# Representation of Scheme data types
#


List   = list         # A Scheme List is implemented as a Python list
Number = (int, float) # A Scheme Number is implemented as a Python int or float
# TODO: String
# TODO: Boolean
# TODO: Port


class Symbol(str):
    """
    A Scheme Symbol.
    """


def sym(s, symbol_table={}):
    """
    Find or create unique Symbol entry for str s in symbol table.
    """
    if s not in symbol_table:
        symbol_table[s] = Symbol(s)
    return symbol_table[s]


_quote = sym("quote")
_if = sym("if")
_set = sym("set!")
_define = sym("define")
_lambda = sym("lambda")
_begin = sym("begin")
_definemacro = sym("define-macro")
_quasiquote = sym("quasiquote")
_unquote = sym("unquote")
_unquotesplicing = sym("unquote-splicing")


#
# Parsing
#


def parse(inport):
    """
    Read a Scheme expression from a string to create AST (list).
    """
    # Backwards compatibility: given a str, convert it to an InPort
    if isinstance(inport, str):
        inport = InPort(io.StringIO(inport))
    return read(inport)


class InPort(object):
    """
    An input port. Retains a line of chars.
    """

    tokenizer = re.compile(r'''
        \s*                 # initial whitespace
        (                   # match group for scheme token
            ,@              # abbrev. for unquote-splicing
          | [()'`,]         # parentheses and quotations (single char. token)
          | "(?:            # start of string expr. (string is token)
                 [\\].      # character escaping
               | [^\\"]     # string content
            )*"
          | ;.*             # comment
          | [^\s('"`,;)]*   # symbol (no whitespace, quotes or commas)
        )
        (.*)                # group for the rest outside of the matched token
        ''', re.VERBOSE)

    def __init__(self, file_obj):
        self.file_obj = file_obj
        self.line = ''

    def next_token(self):
        """
        Return the next token, reading new text into line buffer if needed.
        """
        while True:
            if self.line == "":
                self.line = self.file_obj.readline()
            if self.line == "":
                return eof_object
            token, self.line = InPort.tokenizer.match(self.line).groups()
            if token != "" and not token.startswith(';'):
                return token


eof_object = Symbol("#<eof-object>")  # Note: uninterned; can't be read


def readchar(inport):
    """
    Read the next character from an input port.
    """
    if inport.line != '':
        char = inport.line[0]
        inport.line = inport.line[1:]
        return char
    else:
        return inport.file.read(1) or eof_object


def read(inport):
    """
    Read a Scheme expression from an input port.
    """
    def read_ahead(token):
        if '(' == token:
            ast_list = []
            while True:
                token = inport.next_token()
                if token == ')':
                    return ast_list
                else:
                    ast_list.append(read_ahead(token))
        elif ')' == token:
            raise SyntaxError('unexpected )')
        elif token in quotes:
            return [quotes[token], read(inport)]
        elif token is eof_object:
            raise SyntaxError('unexpected EOF in list')
        else:
            return atom(token)
    # body of read:
    token1 = inport.next_token()
    if token1 is eof_object:
        return eof_object
    else:
        return read_ahead(token1)


quotes = {
    "'": _quote,
    "`": _quasiquote,
    ",": _unquote,
    ",@": _unquotesplicing,
    }


def atom(token):
    """
    Numbers become numbers; #t and #f are booleans; "..." is string; every
    other token is a symbol.
    """
    if token == '#t':
        return True
    elif token == '#f':
        return False
    elif token[0] == '"':
        # TODO: remove encode decode HACK
        return token[1:-1].encode().decode('unicode_escape')
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            try:
                return complex(token.replace('i', 'j', 1))
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
        'display': lambda x: print(to_string(x), end=''),
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
    # TODO: remove HACK (string with variable name is not a symbol)
    if isinstance(x, str):
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

def repl(prompt='lis.py> ', inport=InPort(sys.stdin), out=sys.stdout):
    """
    A prompt-read-eval-print loop.
    """
    while True:
        try:
            if prompt:
                print(prompt, end="", file=sys.stderr, flush=True)
            exp = parse(inport)
            if exp is eof_object:
                print()
                return
            val = eval(exp)
            if val is not None and out:
                print(to_string(val), file=out)
        except Exception as ex:
            print('{}: {}'.format(type(ex).__name__, ex))


def to_string(exp):
    """
    Convert a Python object back into a Scheme-readable string.
    """
    if exp is True:
        return '#t'
    elif exp is False:
        return '#f'
    elif isinstance(exp, Symbol):
        return exp
    elif isinstance(exp, str):
        # TODO: remove encode decode HACK
        return '"{}"'.format(
            x.encode('unicode_escape').decode().replace('"', r'\"'))
    elif isinstance(exp, List):
        return "(" + " ".join(map(to_string, exp)) + ")"
    elif isinstance(exp, complex):
        return str(exp).replace('j', 'i')
    else:
        return str(exp)


def load(filename):
    """
    Eval every expression from a file.
    """
    repl(None, InPort(open(filename)), None)


#
# main
#

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description="Yet Another lispy clone.")
    ap.add_argument("source", nargs='?', help="lispy source code file")
    ap.add_argument(
        "-l", "--load",
        action="store_true",
        help="load source into repl, as if entered line by line")
    args = ap.parse_args()

    if args.source is None:
        repl()
    else:
        with open(args.source, "r") as source_file:
            if args.load:
                for line in source_file:
                    line = line.strip()
                    if len(line) == 0:
                        continue
                    print("lis.py>", line)
                    try:
                        val = eval(parse(line))
                    except Exception as ex:
                        print("error:", ex, file=sys.stderr)
                        repl()
                        sys.exit(1)
                    if val is not None:
                        print(to_string(val))
                repl()
            else:
                source = source_file.read()
                eval(parse(source))
