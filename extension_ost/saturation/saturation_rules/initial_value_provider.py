from typing import Dict, Tuple
from sympy import S, Add, Expr, Mul, Poly, PolynomialError, Pow, Rational, Symbol, oo, powsimp, sqrt, sympify


class InitialValueProvider:
    def __init__(self):
        self.initials: Dict[Symbol, Tuple[Expr, Expr]] = {}

    def _get_sqrts(self, expression):
        powers = expression.atoms(Pow)

        for p in powers:
            if p.exp == S.Half:
                yield p

    def is_nonnegative(self, expr0: Expr):
        # check if positivity can easily shown
        if expr0.is_nonnegative:
            return True
        
        sqrts = list(self._get_sqrts(expr0))
        root_subs = {k: Symbol(f"ROOT_SUBS{i}") for i,k in enumerate(sqrts)}
        expr = expr0.subs(root_subs)

        # if isinstance(expr, Pow) and expr.exp == S.Half:
        #     # this is sound, since we use squareroots only to talk about bounds for absolute values of variables (which are by definition positive)
        #     return True
        
        # try to lower bound the expression, and check if positivity can then be shown
        initial_gens = list(self.initials.keys())+list(root_subs.values())
        diff_expr_poly = Poly(expr, *initial_gens)

        symbolic_monoms = [
            Mul(*[gen**exp for gen, exp in zip(diff_expr_poly.gens, powers)]) 
            for powers in diff_expr_poly.monoms()
        ]
        root_lbs = {monom: S.Zero for monom in symbolic_monoms if monom.free_symbols.isdisjoint(self.initials.keys())}

        coeff_monom_list = [(coeff,Mul(*[var**exp for var, exp in zip(initial_gens, poly_exps)])) for poly_exps, coeff in diff_expr_poly.terms()]

        term = S.Zero
        for coeff, monom in coeff_monom_list:
            if coeff.is_positive:
                monom_bound = root_lbs[monom] if monom in root_lbs else (-oo if len(monom.free_symbols.intersection(root_subs.keys()))>0 else\
                                self._get_lb_for_initial_monomial(monom, root_subs))
                term += monom_bound*coeff
            elif coeff.is_negative:
                monom_bound = oo if monom in root_lbs else (oo if len(monom.free_symbols.intersection(root_subs.keys()))>0 else\
                                self._get_ub_for_initial_monomial(monom, root_subs))
                term += monom_bound*coeff
            else:
                raise ValueError("Coefficient sign must be known")

        if term.simplify().is_nonnegative:
            return True

        return False
    
    def _get_ub_of_pow_of_initial(self, monom: Expr, root_subs):
        monom = monom.expand()
        if monom in self.initials:
            return self.initials[monom][1]
        if not monom.free_symbols.isdisjoint(root_subs.values()):
            return oo

        if isinstance(monom, Pow):
            base = monom.args[0]
            exponent = monom.args[1]
            if base not in self.initials:
                raise KeyError(f"monom base {base} expected to be in initials")
            if exponent.is_odd:
                return self.initials[base][1]**exponent
            if exponent.is_even:
                # take the absolutely larger bound
                if self.initials[base][0].is_nonnegative:
                    return self.initials[base][1]**exponent
                if self.initials[base][1].is_nonpositive:
                    return self.initials[base][0]**exponent
                
                diff_expr = self.initials[base][1]+self.initials[base][0]
                if diff_expr.is_positive:
                    return self.initials[base][1]**exponent
                if diff_expr.is_negative:
                    return self.initials[base][0]**exponent
                # inconclusive :(
                return S.Zero

        raise NotImplementedError(f"monomial {monom} could not be bounded")
    
    def _get_lb_of_pow_of_initial(self, monom: Expr, root_subs):
        monom = monom.expand()
        if monom in self.initials:
            return self.initials[monom][0]
        if len(monom.free_symbols.difference(root_subs.values()))==0:
            return S.Zero
        if isinstance(monom, Pow):
                    base = monom.args[0]
                    exponent = monom.args[1]
                    if base not in self.initials:
                        raise KeyError(f"monom base {base} expected to be in initials")
                    if exponent.is_odd:
                        return self.initials[base][1]**exponent
                    if exponent.is_even:
                        # take the absolutely larger bound
                        if self.initials[base][1].is_nonnegative:
                            return self.initials[base][1]**exponent
                        else:
                            return S.Zero
                        
                        # inconclusive :(

        raise NotImplementedError("monomial could not be bounded")

    def _get_ub_for_initial_monomial(self, monom: Expr, root_subs: Dict[Expr, Expr]):
        # TODO: support more complex monomials, like x0*y0
        if len(monom.free_symbols) == 0:
            return monom
        if len(monom.free_symbols.difference((set(self.initials.keys()).union(root_subs.values()))))!=0:
            raise NotImplementedError(f"Currently only monomials that are of form x**k for some initial variable x are supported, not: {monom}")
        if monom in self.initials:
            return self.initials[monom][1]

        if isinstance(monom, Mul):
            expr = 1
            for elem in monom.args:
                expr*=self._get_ub_of_pow_of_initial(elem, root_subs)
            return expr
            
        return self._get_ub_of_pow_of_initial(monom, root_subs)
    
    def _get_lb_for_initial_monomial(self, monom: Expr, root_subs: Dict[Expr, Expr]):
        # TODO: support more complex monomials, like x0*y0
        if len(monom.free_symbols) == 0:
            return monom
        if len(monom.free_symbols.difference((set(self.initials.keys()).union(root_subs.values()))))!=0:
            raise NotImplementedError(f"Currently only monomials that are of form x**k for some initial variable x are supported, not: {monom}")
        if monom in self.initials:
            return self.initials[monom][0]
        if monom in root_subs:
            return 0 # This is sound, because whenever a rules applies a squareroot, it checks whether the 

        if isinstance(monom, Mul):
            expr = 1
            for elem in monom.args:
                expr*=self._get_lb_of_pow_of_initial(elem, root_subs)
            return expr
            
        return self._get_lb_of_pow_of_initial(monom, root_subs)

    def add_initial(self, symbol, lb=-oo, ub=oo):
        self.initials[symbol] = (lb, ub)

    def are_sqrts_atomic(self, expr):
        powers = expr.atoms(Pow)
        
        for p in powers:
            base, exp = p.args
            if exp == Rational(1, 2):
                if not (base.is_Symbol or base.is_Number):
                    return False
        return True

    def _upper_bound_expression_with_squares(self, expression):
        if(self.are_sqrts_atomic(expression)):
            return expression
        add_args = Add.make_args(expression)
        res = sympify(0)

        for add_part in add_args:
            terms = Mul.make_args(add_part)
            coeff = Mul(*[t for t in terms if t.is_number])
            exp_term = Mul(*[t for t in terms if not t.is_number])
            if not coeff.is_nonnegative:
                return

            if(isinstance(exp_term, Pow) and exp_term.exp == S.Half):
                # take the sqrt of every term in the sqrt
                adds_inside_sqrt = Add.make_args(exp_term.args[0])
                res_inside = sympify(0)
                for add_inside in adds_inside_sqrt:
                    r = powsimp(sqrt(add_inside), force=True)
                    if self.is_nonnegative(add_inside):
                        res_inside += r
                    else:
                        return
                res += res_inside*coeff 
            elif(len([i for i in self._get_sqrts(exp_term)])>0):
                return
            else:
                res += exp_term*coeff
        return res
    
    def asymptotic_sign(self, expr):
        """Takes an expression over multiple variables and checks for the variable(s) with the highest degree for their asymptotic 

        Examples:
        asymptotic_nonnegative(sympify("2x**2 -y +z+3")) -> 1
        asymptotic_nonnegative(sympify("0")) -> 1
        asymptotic_nonnegative(sympify("-2xy + 2x**2")) -> 1
        asymptotic_nonnegative(sympify("-2y**2 + 2x**2")) -> 0
        asymptotic_nonnegative(sympify("-2y**2 - 2x**2")) -> -1
        asymptotic_nonnegative(sympify("-2y**2 + 2x**2*y")) -> 1
        asymptotic_nonnegative(sympify("-2y**2 + 2x**2*sqrt(x)")) -> 1
        
        Args:
            expr (_type_): _description_
        """

        expr = sympify(expr).expand()
        if expr.is_zero:
            return 1
        terms = Add.make_args(expr)
        
        max_key = None
        max_terms = []
        
        for term in terms:
            degrees = []
            for base, exp in term.as_powers_dict().items():
                if base.free_symbols:
                    degrees.append(exp)
            # x**3 * y**2 * sqrt(z) -> (3, 2, 1/2)
            key = tuple(sorted(degrees, reverse=True))

            if max_key is None or key > max_key:
                max_key = key
                max_terms = [term]
            elif key == max_key:
                max_terms.append(term)

        if all(self.is_nonnegative(term) for term in max_terms):
            return 1
        if all(self.is_nonnegative(-term) for term in max_terms):
            return -1
        return 0