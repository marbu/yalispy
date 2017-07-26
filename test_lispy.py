# -*- coding: utf8 -*-


import lispy


def test_tokenize():
    program = "(begin (define r 10) (* pi (* r r)))"
    tokens = ["(", "begin", "(", "define", "r", "10", ")", "(", "*", "pi", "(", "*", "r", "r", ")", ")", ")"]
    assert lispy.tokenize(program) == tokens


def test_parse():
    program = "(begin (define r 10) (* pi (* r r)))"
    ast = ["begin", ["define", "r", 10], ["*", "pi", ["*", "r", "r"]]]
    assert lispy.parse(program) == ast
