(define circle-area (lambda (r) (* pi (* r r))))
(circle-area 3)

(define make-account (lambda (balance) (lambda (amt) (begin (set! balance (+ balance amt)) balance))))
(define account1 (make-account 100.00))
(account1 -20.00)

(define fact (lambda (n) (if (<= n 1) 1 (* n (fact (- n 1))))))
(fact 10)
(fact 100)

(circle-area (fact 10))

(define count (lambda (item L) (if L (+ (equal? item (car L)) (count item (cdr L))) 0)))
(count 0 (list 0 1 2 3 0 0))
(count (quote the) (quote (the more the merrier the bigger the better)))

(define twice (lambda (x) (* 2 x)))
(twice 5)

(define repeat (lambda (f) (lambda (x) (f (f x)))))
((repeat twice) 10)
((repeat (repeat twice)) 10)
((repeat (repeat (repeat twice))) 10)

(pow 2 16)

(define fib (lambda (n) (if (<= n 1) 1 (+ (fib (- n 1)) (fib (- n 2))))))
(define range (lambda (a b) (if (= a b) (quote ()) (cons a (range (+ a 1) b)))))
(range 0 10)
(map fib (range 0 10))
