# -*- coding: utf8 -*-


import pytest

import lispy


def test_tokenize():
    program = "(begin (define r 10) (* pi (* r r)))"
    tokens = ["(", "begin", "(", "define", "r", "10", ")", "(", "*", "pi", "(", "*", "r", "r", ")", ")", ")"]
    assert lispy.tokenize(program) == tokens


def test_parse():
    program = "(begin (define r 10) (* pi (* r r)))"
    ast = ["begin", ["define", "r", 10], ["*", "pi", ["*", "r", "r"]]]
    assert lispy.parse(program) == ast


def test_eval_variable():
    env = lispy.standard_env()
    env["foo"] = 10
    assert eval("foo", env) == 10


def test_eval_number():
    assert lispy.eval(10) == 10
    assert lispy.eval(1.5) == 1.5


def test_eval_conditional():
    assert lispy.eval(lispy.parse("(if (> 1 0) (+ 1 1) (- 1 1))")) == 2
    assert lispy.eval(lispy.parse("(if (< 1 0) (+ 1 1) (- 1 1))")) == 0


def test_eval_definition():
    env = lispy.standard_env()
    assert "foo" not in env
    lispy.eval(lispy.parse("(define foo (+ 1 2))"), env)
    assert env["foo"] == 3


def test_eval_fullexample():
    env = lispy.standard_env()
    lispy.eval(["define", "r", 10], env)
    assert lispy.eval(["*", "pi", ["*", "r", "r"]], env) == 314.1592653589793


@pytest.mark.parametrize("program", [
    "()",
    "(begin (define r 10) (* pi (* r r)))",
    "(if (> 1 0) (+ 1 1) (- 1 1))",
    ])
def test_schemestr(program):
    assert lispy.schemestr(lispy.parse(program)) == program
