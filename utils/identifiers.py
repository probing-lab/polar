__count_unique_var = 0


def get_unique_var(name="u"):
    """
    Returns a unique identifier which can be used as a program variable
    """
    global __count_unique_var
    var = "_" + name + str(__count_unique_var)
    __count_unique_var += 1
    return var
