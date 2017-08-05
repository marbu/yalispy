# -*- coding: utf8 -*-


import pytest

import yalispy


def test_tokenize():
    program = "(begin (define r 10) (* pi (* r r)))"
    tokens = ["(", "begin", "(", "define", "r", "10", ")", "(", "*", "pi", "(", "*", "r", "r", ")", ")", ")"]
    assert yalispy.tokenize(program) == tokens


def test_parse():
    program = "(begin (define r 10) (* pi (* r r)))"
    ast = ["begin", ["define", "r", 10], ["*", "pi", ["*", "r", "r"]]]
    assert yalispy.parse(program) == ast


def test_eval_variable():
    env = yalispy.standard_env()
    env["foo"] = 10
    assert yalispy.eval("foo", env) == 10


def test_eval_number():
    assert yalispy.eval(10) == 10
    assert yalispy.eval(1.5) == 1.5


def test_eval_quote():
    env = yalispy.standard_env()
    assert 'r' not in env
    assert yalispy.eval(['quote', ["*", "pi", ["*", "r", "r"]]], env) == ["*", "pi", ["*", "r", "r"]]


def test_eval_quote_str():
    assert yalispy.schemestr(yalispy.eval(yalispy.parse('(quote (* 3 r))'))) == '(* 3 r)'


def test_eval_conditional():
    assert yalispy.eval(yalispy.parse("(if (> 1 0) (+ 1 1) (- 1 1))")) == 2
    assert yalispy.eval(yalispy.parse("(if (< 1 0) (+ 1 1) (- 1 1))")) == 0


def test_eval_definition():
    env = yalispy.standard_env()
    assert "foo" not in env
    yalispy.eval(yalispy.parse("(define foo (+ 1 2))"), env)
    assert env["foo"] == 3


def test_eval_fullexample():
    env = yalispy.standard_env()
    yalispy.eval(["define", "r", 10], env)
    assert yalispy.eval(["*", "pi", ["*", "r", "r"]], env) == 314.1592653589793


@pytest.mark.parametrize("program", [
    "()",
    "(begin (define r 10) (* pi (* r r)))",
    "(if (> 1 0) (+ 1 1) (- 1 1))",
    ])
def test_schemestr(program):
    assert yalispy.schemestr(yalispy.parse(program)) == program
