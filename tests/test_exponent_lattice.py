import unittest
from sympy import sympify
from invariants.exponent_lattice import ExponentLattice


class ExponentLatticeTest(unittest.TestCase):

    def test_basis_1(self):
        n1 = sympify("2")
        n2 = sympify("1/2")
        lattice = ExponentLattice([n1, n2])
        basis = lattice.compute_basis()
        self.assertTrue(ExponentLattice.bases_are_equivalent(basis, [[1, 1]]))

    def test_basis_2(self):
        n1 = sympify("1")
        n2 = sympify("-1")
        lattice = ExponentLattice([n1, n2])
        basis = lattice.compute_basis()
        self.assertTrue(ExponentLattice.bases_are_equivalent(basis, [[1, 0], [0, -2]]))

    def test_basis_3(self):
        n1 = sympify("CRootOf('x**2 + 1', 0)")
        n2 = sympify("CRootOf('x**2 + 1', 1)")
        lattice = ExponentLattice([n1, n2])
        basis = lattice.compute_basis()
        self.assertTrue(ExponentLattice.bases_are_equivalent(basis, [[1, 1], [4, 0]]))

    def test_basis_4(self):
        n1 = sympify("2")
        n2 = sympify("1/2")
        n3 = sympify("1")
        n4 = sympify("-1")
        n5 = sympify("CRootOf('x**2 + 1', 0)")
        n6 = sympify("CRootOf('x**2 + 1', 1)")
        lattice = ExponentLattice([n1, n2, n3, n4, n5, n6])
        basis = lattice.compute_basis()
        expected_basis = [[1, 1, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0], [0, 0, 0, 1, 0, 2], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 0, 4]]
        self.assertTrue(ExponentLattice.bases_are_equivalent(basis, expected_basis))

    def test_basis_5(self):
        n1 = sympify("sqrt(2)")
        n2 = sympify("sqrt(3)")
        lattice = ExponentLattice([n1, n2])
        basis = lattice.compute_basis()
        self.assertEqual(basis, [])

    def test_basis_6(self):
        n1 = sympify("1 + sqrt(2)")
        n2 = sympify("1 - sqrt(2)")
        n3 = sympify("3")
        n4 = sympify("5")
        lattice = ExponentLattice([n1, n2, n3, n4])
        basis = lattice.compute_basis()
        expected_basis = [[2, 2, 0, 0]]
        self.assertTrue(ExponentLattice.bases_are_equivalent(basis, expected_basis))
