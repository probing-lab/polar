from symengine.lib.symengine_wrapper import Matrix, eye, Symbol


def characteristic_poly(matrix: Matrix):
    t = Symbol("t")
    return ((eye(matrix.cols)*t) - matrix).det().simplify(), t
