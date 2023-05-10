_count_unique_var = 0


def get_unique_var(name="u"):
    """
    Returns a unique identifier which can be used as a program variable
    """
    global _count_unique_var
    var = "_" + name + str(_count_unique_var)
    _count_unique_var += 1
    return var
