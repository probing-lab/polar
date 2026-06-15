from typing import Dict, Tuple
from sympy import S, Expr, Mul, Poly, PolynomialError, Pow, Symbol, oo


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
                                self._get_lb_for_initial_monomial(monom))
                term += monom_bound*coeff
            elif coeff.is_negative:
                monom_bound = oo if monom in root_lbs else (oo if len(monom.free_symbols.intersection(root_subs.keys()))>0 else\
                                self._get_ub_for_initial_monomial(monom))
                term += monom_bound*coeff
            else:
                raise ValueError("Coefficient sign must be known")

        if term.simplify().is_nonnegative:
            return True

        return False
    
    def _get_ub_of_pow_of_initial(self, monom: Expr):
        monom = monom.expand()
        if monom in self.initials:
            return self.initials[monom][1]

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
    
    def _get_lb_of_pow_of_initial(self, monom: Expr):
        monom = monom.expand()
        if monom in self.initials:
            return self.initials[monom][0]
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

    def _get_ub_for_initial_monomial(self, monom: Expr):
        # TODO: support more complex monomials, like x0*y0
        if len(monom.free_symbols) == 0:
            return monom
        if len(monom.free_symbols.difference(self.initials.keys()))!=0:
            raise NotImplementedError("Currently only monomials that are of form x**k for some initial variable x are supported")
        if monom in self.initials:
            return self.initials[monom][1]

        if isinstance(monom, Mul):
            expr = 1
            for elem in monom.args:
                expr*=self._get_ub_of_pow_of_initial(elem)
            return expr
            
        return self._get_ub_of_pow_of_initial(monom)
    
    def _get_lb_for_initial_monomial(self, monom: Expr):
        # TODO: support more complex monomials, like x0*y0
        if len(monom.free_symbols) == 0:
            return monom
        if len(monom.free_symbols.difference(self.initials.keys()))!=0:
            raise NotImplementedError(f"Currently only monomials that are of form x**k for some initial variable x are supported, not: {monom}")
        if monom in self.initials:
            return self.initials[monom][0]

        if isinstance(monom, Mul):
            expr = 1
            for elem in monom.args:
                expr*=self._get_lb_of_pow_of_initial(elem)
            return expr
            
        return self._get_lb_of_pow_of_initial(monom)

    def add_initial(self, symbol, lb=-oo, ub=oo):
        self.initials[symbol] = (lb, ub)