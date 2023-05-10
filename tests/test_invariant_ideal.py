import unittest
from typing import Set

from invariants import InvariantIdeal
from sympy import sympify, Symbol, Expr


class InvariantIdealTest(unittest.TestCase):
    def test_basis_1(self):
        closed_forms = {
            "v": "1",
            "w": "1",
            "x": "n/2 + 1",
            "y": "n/2 + 1",
        }
        expected_basis = {"v - 1", "w - 1", "-x + y"}
        self.__test_basis__(closed_forms, expected_basis)

    def test_basis_2(self):
        closed_forms = {
            "x": "n + 2**(n+2) - n**2*2**n + 3**n",
            "y": "n + 2**(2*n) - 3**n + n*3**n",
        }
        self.__test_basis__(closed_forms, [])
        # TODO remove test: only for developing

    def __test_basis__(self, closed_forms, expected_basis):
        n = Symbol("n", integer=True)
        closed_forms = {
            s: sympify(cf).xreplace({Symbol("n"): n}) for s, cf in closed_forms.items()
        }
        expected_basis = {sympify(poly) for poly in expected_basis}
        ideal = InvariantIdeal(closed_forms)
        basis = ideal.compute_basis()
        self.assertEqual(len(basis), len(expected_basis))
        for poly in basis:
            self.assertTrue(self.__expr_is_in_set__(poly, basis))

    @staticmethod
    def __expr_is_in_set__(expr: Expr, es: Set[Expr]):
        for e in es:
            if (e - expr).expand() == 0:
                return True
        return False


if __name__ == "__main__":
    unittest.main()
