# -*- coding: utf8 -*-


import io
import textwrap

import pytest

import yalispy


@pytest.fixture
def env():
    return yalispy.standard_env()


@pytest.mark.parametrize("source,tokens_expected", [
    (
        "",
        []),
    (
        "    ",
        []),
    (
        "; some comment",
        []),
    (
        "'`,,@,",
        ["'", "`", ",", ",@", ","]),
    (
        "foo->bar!",
        ["foo->bar!"]),
    (
        ",@(* 2 345)",
        [",@", "(", "*", "2", "345", ")"]),
    (
        "(if #t (newline))",
        ["(", "if", "#t", "(", "newline", ")", ")"]),
    (
        '  ( display  "Hello World! " )  ',
        ["(", "display", '"Hello World! "', ")"]),
    (
        '''(foo->bar "\\"Go!\\"")''',
        ["(", "foo->bar", '"\\"Go!\\""', ")"]),
    (
        "(begin (define r 10) (* pi (* r r))) ; comment",
        [
            "(", "begin",
            "(", "define", "r", "10", ")",
            "(", "*", "pi", "(", "*", "r", "r", ")", ")",
            ")"]),
    ])
def test_tokenizer(source, tokens_expected):
    source_file = io.StringIO(initial_value=source)
    inport = yalispy.InPort(source_file)
    tokens = []
    while True:
        token = inport.next_token()
        if token == yalispy.eof_object:
            break
        tokens.append(token)
    assert tokens == tokens_expected


def test_parse():
    program = "(begin (define r 10) (* pi (* r r)))"
    ast = ["begin", ["define", "r", 10], ["*", "pi", ["*", "r", "r"]]]
    assert yalispy.parse(program) == ast


def test_eval_variable(env):
    env["foo"] = 10
    assert yalispy.eval("foo", env) == 10


def test_eval_number():
    assert yalispy.eval(10) == 10
    assert yalispy.eval(1.5) == 1.5


def test_eval_quote(env):
    assert 'r' not in env
    assert yalispy.eval(['quote', ["*", "pi", ["*", "r", "r"]]], env) == ["*", "pi", ["*", "r", "r"]]


def test_eval_quote_str():
    assert yalispy.to_string(yalispy.eval(yalispy.parse('(quote (* 3 r))'))) == '(* 3 r)'


def test_eval_conditional():
    assert yalispy.eval(yalispy.parse("(if (> 1 0) (+ 1 1) (- 1 1))")) == 2
    assert yalispy.eval(yalispy.parse("(if (< 1 0) (+ 1 1) (- 1 1))")) == 0


def test_eval_definition(env):
    assert "foo" not in env
    assert yalispy.eval(yalispy.parse("(define foo (+ 1 2))"), env) is None
    assert env["foo"] == 3


def test_eval_fullexample(env):
    assert yalispy.eval(["define", "r", 10], env) is None
    assert yalispy.eval(["*", "pi", ["*", "r", "r"]], env) == 314.1592653589793


@pytest.mark.parametrize("program", [
    "()",
    "(begin (define r 10) (* pi (* r r)))",
    "(if (> 1 0) (+ 1 1) (- 1 1))",
    ])
def test_to_string(program):
    assert yalispy.to_string(yalispy.parse(program)) == program


def test_function_defcall_circle(env):
    func_prog = "(define circle-area (lambda (r) (* pi (* r r))))"
    call_prog = "(circle-area 10)"
    assert yalispy.eval(yalispy.parse(func_prog), env) is None
    assert yalispy.eval(yalispy.parse(call_prog), env) == 314.1592653589793


def test_function_defcall_account(env):
    func_prog = textwrap.dedent("""\
        (begin
            (define make-account
                (lambda (balance)
                    (lambda (amt)
                        (begin (set! balance (+ balance amt))
                               balance))))
            (define account1 (make-account 100.00))
            (account1 -20.00))
        """)
    assert yalispy.eval(yalispy.parse(func_prog)) == 80


def test_function_defcall_fact(env):
    func_prog = "(define fact (lambda (n) (if (<= n 1) 1 (* n (fact (- n 1))))))"
    assert yalispy.eval(yalispy.parse(func_prog), env) is None
    assert yalispy.eval(yalispy.parse("(fact 10)"), env) == 3628800


def test_function_defcall_count(env):
    func_prog = textwrap.dedent("""\
        (begin
            (define count
                (lambda (item L)
                    (if L
                        (+ (equal? item (car L)) (count item (cdr L)))
                        0)))
            (count 0 (list 0 1 2 3 0 0)))
        """)
    assert yalispy.eval(yalispy.parse(func_prog)) == 3
