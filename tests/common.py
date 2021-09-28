from sympy import Piecewise


def get_test_specs(filename, spec_id):
    specs = []
    starts_with = "#test: " + spec_id + ";"
    with open(filename, "r") as file:
        for line in file:
            if line.startswith(starts_with):
                line = line[len(starts_with):]
                spec = [d.strip() for d in line.split(";")]
                specs.append(spec)
    return specs


def unpack_general_form(maybe_piecewise):
    if not isinstance(maybe_piecewise, Piecewise):
        return maybe_piecewise

    for expr, cond in maybe_piecewise.args:
        if cond.is_Boolean and bool(cond):
            return expr

    raise RuntimeError("Encountered Piecewise without general expression.")
