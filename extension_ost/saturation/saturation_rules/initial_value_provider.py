from functools import cache
from typing import Dict, Tuple
from sympy import S, Abs, Add, Expr, Mul, Poly, PolynomialError, Pow, Rational, Symbol, factor, oo, powsimp, sqrt, sympify


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
        if isinstance(expr0, Abs):
            return True
        if isinstance(expr0, Pow) and expr0.exp==S.Half:
            return True
        
        grouped_terms = self._group_terms(expr0.expand().simplify())
        bounding_expression = S.Zero
        if len(grouped_terms.keys())>1:
            pass
        for var_part, coeff in grouped_terms.items():
            if coeff.is_nonnegative:
                lb = self._get_lb_of_monom(var_part)
                bounding_expression+=lb*coeff
            elif coeff.is_nonpositive:
                ub = self._get_ub_of_monom(var_part)
                bounding_expression += ub*coeff
            else:
                raise Exception(f"sign of coefficient is unknown (but expected to be a constant): {coeff}")
        if bounding_expression.is_nonnegative:
            return True
        
    def _get_lb_of_monom(self, expr):
        final_lb = S.One
        mul_args = Mul.make_args(expr)
        assert len(mul_args)>0
        for var in mul_args:
            final_lb*=self._get_lb_of_pow_of_initial(var)
        return final_lb
    
    def _get_ub_of_monom(self, expr):
        final_ub = S.One
        mul_args = Mul.make_args(expr)
        assert len(mul_args)>0
        for var in mul_args:
            final_ub*=self._get_ub_of_pow_of_initial(var)
        return final_ub
    
    def _get_ub_of_pow_of_initial(self, monom: Expr):
        monom = monom.expand()
        if monom.is_number:
            return monom
        if monom in self.initials:
            return self.initials[monom][1]
        if isinstance(monom, Abs):
            return max(abs(self.initials[monom][0],self.initials[monom][1]))

        if isinstance(monom, Pow):
            base = monom.args[0]
            exponent = monom.args[1]
            if base not in self.initials:
                raise KeyError(f"monom base {base} expected to be in initials")
            if exponent == S.Half:
                return sqrt(self._get_ub_of_pow_of_initial(base))
            elif exponent.is_odd:
                return self.initials[base][1]**exponent
            elif exponent.is_even:
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
            else: 
                raise Exception(f"Unknown exponent: {exponent}")

        raise NotImplementedError(f"monomial {monom} could not be bounded")
    
    def _get_lb_of_pow_of_initial(self, monom: Expr):
        monom = monom.expand()
        if monom.is_number:
            return monom
        if monom in self.initials:
            return self.initials[monom][0]
        if isinstance(monom, Abs):
            return 0 # this can be improved in some cases

        if isinstance(monom, Pow):
            base = monom.args[0]
            exponent = monom.args[1]
            if base not in self.initials:
                raise KeyError(f"monom base {base} expected to be in initials")
            elif exponent == S.Half:
                return sqrt(self._get_lb_of_pow_of_initial(base))
            elif exponent.is_odd:
                return self.initials[base][1]**exponent
            elif exponent.is_even:
                # take the absolutely larger bound
                if self.initials[base][1].is_nonnegative:
                    return self.initials[base][1]**exponent
                else:
                    return S.Zero
            else:
                raise Exception(f"Unknown exponent: {exponent}")

        raise NotImplementedError(f"monomial could not be bounded: {monom}")

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
    
    def _use_abs_subadditivity(self, expression):
        if(isinstance(expression, Abs)):
            res = S.Zero
            for summand in Add.make_args(expression.args[0]):
                res += Abs(summand)
            return res.simplify()
        else:
            return expression

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
                    # r_inner = self._use_abs_subadditivity(Abs(add_inside).simplify())
                    if(add_inside.is_negative):
                        return
                    r = powsimp(sqrt(add_inside))
                    r = self._use_abs_subadditivity(r)
                    res_inside += factor(r, deep=True)
                res += res_inside*coeff 
            elif(len([i for i in self._get_sqrts(exp_term)])>0):
                return
            else:
                res += exp_term*coeff
        return res
    
    def _group_terms(self, expr) -> Dict[Expr, Expr]:
        symbols = expr.free_symbols
        terms = Add.make_args(expr)
        
        grouped_terms = {}
        for term in terms:
            coeff, var_part = term.as_independent(*symbols, as_Add=False)
            
            if var_part in grouped_terms:
                grouped_terms[var_part] += coeff
            else:
                grouped_terms[var_part] = coeff
        return grouped_terms

    @cache
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
        if len([s for s in self._get_sqrts(expr)]):
            pass
        if expr.is_zero:
            return 1


        max_key = None
        max_terms = []
        grouped_terms = self._group_terms(expr)
        
        for var_part,coeff in grouped_terms.items():
            term = coeff*var_part
            if term.is_zero:
                continue
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
        print(f"Unable to check asymptotic behavior: {expr}")
        return 0