import random


def get_unique_name(existing_values, base):
    while base in existing_values:
        base += str(random.randint(0, 9))
    return base
