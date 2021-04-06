
__count_unique_var = 0


def get_unique_var():
    global __count_unique_var
    var = "_u" + str(__count_unique_var)
    __count_unique_var += 1
    return var
