from diofant import Symbol


class Assignment:

    def __init__(self, variable: Symbol, value, context):
        self.variable = variable
        self.value = value
        self.context = context
