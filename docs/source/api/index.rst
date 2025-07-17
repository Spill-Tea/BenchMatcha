PyTemplate API Documentation
============================

PyTemplate API documentation.

Here are python and cython code snippets to demonstrate the use of respective customized
lexers with custom syntax highlighting style. These examples are not necessarily meant
to be fully valid code, but to demonstrate key features not available through standard
pygments syntax highlighting styles.

Python Example Snippet
----------------------

.. code-block:: python
   :caption: example.py

   #!/usr/bin/env python3
   """Module level docstring."""
   from typing import ClassVar
   import numpy as np

   CONSTANT_A: int = 0xFF
   CONSTANT_B: float = np.pi

   # NOTE: this is an example class
   class Example(object):
       """Example docstring.

       Args:
            arg1 (str): argument 1
            arg2 (int): argument 2

       Attributes:
            data (dict): data

       """
       arg1: str
       arg2: int
       data: dict
       seventeen: ClassVar[list[int]] = [17, 0x11, 0o21, 0b10001]
       other: ClassVar[list[int]] = [1e-5, 1.0e+3, 2j, 2l, 2.7E4J]

       def __init__(self, arg1: str, arg2: int) -> None:
           self.arg1 = arg1
           self.arg2 = arg2
           self.data = {
               "a": [(1, 2, (3, 4, 5)), (6, 7, (8, 9 , 10))],
               "b": {"c": (7, 4, 3), "d": {"e", "f", "g"}},
           }

       def __getattr__(self, value):
           return self.method(value)

       def method(self, value):
           return self.data[value]

       def write(self, text):
           print(f"{text:<5}\n")

       def do_something(self, value):
           if value > CONSTANT_A:
               return value - CONSTANT_B
           else:
               return value + 0b10011


Cython Example Snippet
----------------------

.. code-block:: cython
   :caption: example.pyx

    """Module level docstring."""
    import cython
    from libc.stdlib cimport free, malloc

    cdef extern from "<vector>" namespace "std":
        cdef cppclass vector[T]:
            vector()
            T& operator[](int)

    ctypedef fused StringTypeObject:
        str
        bytes

    ctypedef struct CustomStruct:
        int y
        str z

    cdef packed struct Breakfast:
        int[4] spam
        signed char[5] eggs

    cdef enum CheeseType:
        manchego = 1
        gouda = 2
        camembert = 3

    cdef union MyUnion:
        int i
        float f
        char c

    cdef inline unsigned char* function(bint flag) noexcept:
        cdef:
            Py_ssize_t j
            unsigned char* k = NULL

        k = <unsigned char*> malloc(5 * sizeof(unsigned char))

        for j in range(5):
            k[j] = "A"

        return k

    # XXX: this is an example class
    cdef class Example:
        """The little example class that couldn't.

        Args:
            arg1 (unsigned long long): ...
            arg2 (double): ...

        """
        cdef public unsigned long long v
        cdef readonly double k
        cdef char* mem

        def __cinit__(self, unsigned long long arg1, double arg2):
            self.v = arg1
            self.k = arg2
            self.mem = <char*> malloc(5 * sizeof(char))

        def __dealloc__(self):
            free(self.mem)

        @cython.boundscheck(False)
        cdef char index(self, size_t idx):
            return self.mem[idx]

    # just an example of nested parenthesis to demonstrate rainbow coloring
    cdef dict obj = {
        "a": [(1, 2, (3, 4, 5)), (6, 7, (8, 9 , 10))],
        "b": {"c": (7, 4, 3), "d": {"e", "f", "g"}},
    }
    cdef tuple builtin_constants  = (True, False, NULL, None,)


.. toctree::
   :caption: Submodules


.. autosummary::
   :toctree: generated
   :recursive:
