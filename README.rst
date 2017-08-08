===================
 Yet Another lispy
===================

This is just another repository with simple `Scheme`_ interpreter written in
Python following `Peter Norvig`_'s essays:

* `(How to Write a (Lisp) Interpreter (in Python))`_.
* `(An ((Even Better) Lisp) Interpreter (in Python))`_.


Examples
========

Loading some lispy scheme source file into repl::

    $ cat example.scm
    (define circle-area (lambda (r) (* pi (* r r))))
    (circle-area 3)
    $ ./yalispy.py -l example.scm
    lis.py> (define circle-area (lambda (r) (* pi (* r r))))
    lis.py> (circle-area 3)
    28.274333882308138
    lis.py>


.. _`Scheme`: https://en.wikipedia.org/wiki/Scheme_%28programming_language%29
.. _`Peter Norvig`: http://norvig.com/
.. _`(How to Write a (Lisp) Interpreter (in Python))`: http://norvig.com/lispy.html
.. _`(An ((Even Better) Lisp) Interpreter (in Python))`: http://norvig.com/lispy2.html
