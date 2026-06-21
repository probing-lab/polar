
import csv
from typing import Dict, List, Tuple
from sympy import S, Expr, GreaterThan, LessThan, Poly, StrictGreaterThan, StrictLessThan, Symbol, oo, solve_univariate_inequality, sympify
from extension_ost.helpers import Expexted
from extension_ost.saturation.saturation_based_bound_computation import compute_bounds_saturation
from extension_ost.saturation.saturation_rules.value_node import ValueNode
from inputparser.parser import Parser
from program.assignment.dist_assignment import DistAssignment
from program.condition.true_cond import TrueCond
from program.program import Program
from program.transformer import normalize_program
from recurrences.rec_builder import RecBuilder

def _extract_bound_from_ineq(ineq: Expr,
                             cop: str,
                             lbs: List[Tuple[str, int]],
                             ubs: List[Tuple[str, int]],
                             recurrence_builder: RecBuilder):
    ineq = Poly(ineq)
    assert ineq.degree() == 1
    var = ineq.gen
    if cop in ("<", "<="):
        ineq = ineq.as_expr() < S(0) 
    elif cop in (">", ">="):
        ineq = ineq.as_expr() > S(0) 
    else:
        raise Exception(f"Unsupported Loop Guard: {cop}")
    solved_ineq = solve_univariate_inequality(ineq, var, relational=True)
    
    if solved_ineq.lhs == var:
        lbs.append((str(var), solved_ineq.rhs)) # the negated loop guard (for x_T)
        ubs.append((str(recurrence_builder.get_initial_value(var)), solved_ineq.rhs)) # the positive loop guard (for x0)
    elif solved_ineq.rhs == var:
        ubs.append((str(var), solved_ineq.lhs))
        lbs.append((str(recurrence_builder.get_initial_value(var)), solved_ineq.lhs))
    else:
        raise Exception(f"Unsupported inequality: {solved_ineq}")
    return var
    
def _depends_on_unbound_support_dist(var: Symbol, normalized_program: Program):
    ancestors = normalized_program.dependency_info[var].ancestors
    for assignment in normalized_program.loop_body:
        if(isinstance(assignment, DistAssignment)) and assignment.variable in ancestors:
            for sup in assignment.get_support():
                if isinstance(sup, Expr):
                    if not sup.is_finite:
                        return True
                else:
                    lb, ub = sup
                    if not lb.is_finite or not ub.is_finite:
                        return True
    return False

def _get_jb_size(var: Symbol, normalized_program: Program):
    # rather proprietary, might fail
    anc_jb_size = list(_get_jb_size(v, normalized_program)+1 for v in normalized_program.dependency_info[var].ancestors.intersection(normalized_program.original_variables) if v != var and v not in normalized_program.dist_variables)
    anc_jb_size.append(1) # this assumes that every var is nonconstant - since we consider only iter-dep. vars, this is true
    return max(anc_jb_size)

def moment_bound_using_ost(file_path: str,
                           lbs: List[Tuple[str, int]],
                           ubs: List[Tuple[str, int]],
                           stopping_time_moment_finite: int,
                           use_minkovski = False,
                           num_sparsest_solutions = 20,
                           keep_nonoptimal_martingales = False,
                           solver_name = "CBC",
                           csv_path = None,
                           num_runs = 1,
                           iter_var = "k"):

    program = Parser().parse_file(file_path)
    lg = program.loop_guard
    print(f"Loop guard: {lg}")

    program.loop_guard = TrueCond()

    normalized_program = normalize_program(program)
    recurrence_builder = RecBuilder(normalized_program)
    lg_var = _extract_bound_from_ineq(lg.poly1-lg.poly2, lg.cop, lbs, ubs, recurrence_builder)       
    lg_depends_on_unbounded_support = _depends_on_unbound_support_dist(lg_var, normalized_program)

    deterministic_vars = set()
    random_vars = set()

    for var in normalized_program.original_variables:
        if not normalized_program.is_iteration_dependent(var):
            continue
        for rv in normalized_program.dist_variables:
            if rv in normalized_program.dependency_info[var].ancestors:
                random_vars.add(Symbol(str(var), real=True))
                continue
        deterministic_vars.add(Symbol(str(var), real=True))
    deterministic_vars = deterministic_vars.difference(random_vars)

    result: Dict[Expr, List[ValueNode]] = {}

    lbs = dict(lbs)
    ubs = dict(ubs)

    lower_bounds_after_termination: Dict[Symbol, Expr] = dict()
    upper_bounds_after_termination: Dict[Symbol, Expr] = dict()
    initial_values: List[Tuple[Symbol, Expr, Expr]] = []
    program_vars: Dict[Symbol, int] = dict()

    subs =  {str(v):v for v in deterministic_vars.union(random_vars)}

    for monom, ub in ubs.items():
        if monom.startswith("E(") and monom.endswith(")"):
            m = sympify(monom[2:-1]).subs(subs)
            upper_bounds_after_termination[Expexted(m)] = sympify(ub).simplify()
        else:
            m = sympify(monom).subs(subs)
            if len(m.free_symbols.difference(deterministic_vars.union(random_vars)))==0:
                upper_bounds_after_termination[m] = sympify(ub).simplify()

    for monom, lb in lbs.items():
        if monom.startswith("E(") and monom.endswith(")"):
            m = sympify(monom[2:-1]).subs(subs)
            lower_bounds_after_termination[Expexted(m)] = sympify(lb).simplify()
        else:
            m = sympify(monom).subs(subs)
            if len(m.free_symbols.difference(deterministic_vars.union(random_vars)))==0:
                lower_bounds_after_termination[m] = sympify(lb).simplify()


    for var in deterministic_vars.union(random_vars):
        if str(var) == iter_var:
            lower_bounds_after_termination[var] = S.One
        # get_jb_size
        size = _get_jb_size(var, normalized_program)
        program_vars[Symbol(str(var), real=True)]=size

        # check for initial_value
        lb = -oo
        ub = oo
        initial = recurrence_builder.get_initial_value(var)
        if initial.is_number:
            continue
        if str(initial) in lbs:
            lb = lbs[str(initial)]
        if str(initial) in ubs:
            ub = ubs[str(initial)]
        if lb.is_nonnegative:
            initial_values.append((Symbol(str(initial), finite=True, real=True, nonnegative=True), lb, ub))
        else:
            initial_values.append((Symbol(str(initial), finite=True, real=True), lb, ub))



    res = compute_bounds_saturation(random_vars,
            deterministic_vars,
            stopping_time_moment_finite - (1 if lg_depends_on_unbounded_support else 0),
            program_vars,
            recurrence_builder,
            initial_values,
            lower_bounds_after_termination,
            upper_bounds_after_termination,
            num_sparsest_solutions=num_sparsest_solutions,
            use_minkowski=use_minkovski,
            keep_non_optimal_martingales=keep_nonoptimal_martingales,
            solver_name=solver_name)
    result = {key: result.get(key,[])+ ([res[key]] if key in res else []) for key in res.keys() | result.keys()}
    

    if csv_path:
        with open(csv_path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(("monomial", "", "bound"))
            for expr, bounds in sorted(result.items(), key=lambda x: str(x[0])):
                ubs = set.union(*({ub.value for ub in b.get_ubs_simplified()} for b in bounds))
                lbs = set.union(*({lb.value for lb in b.get_lbs_simplified()} for b in bounds))
                for ub in sorted(ubs, key=lambda x: str(x)):
                    writer.writerow((str(expr), "<=", str(ub)))
                for lb in sorted(lbs, key=lambda x: str(x)):
                    writer.writerow((str(expr), ">=", str(lb)))
