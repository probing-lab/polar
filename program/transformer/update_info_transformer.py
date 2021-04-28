from .transformer import Transformer
from program import Program


class UpdateInfoTransformer(Transformer):
    """
    Prepares some final data about the program. So it can be better processed afterwards.
    The transformer requires that the passed program is already flattened, meaning does not contain any if-statements.
    """
    program: Program

    def execute(self, program: Program) -> Program:
        self.program = program

        variables_initial = self.__get_all_variables__(self.program.initial)
        variables_body = self.__get_all_variables__(self.program.loop_body)
        program.variables = set(variables_initial) | set(variables_body)
        program.var_to_index = {v: i for i, v in enumerate(variables_body)}
        program.index_to_var = {i: v for i, v in enumerate(variables_body)}

        symbols = self.__get_all_symbols__(program.initial)
        symbols = symbols.union(self.__get_all_symbols__(program.loop_body))
        program.symbols = symbols.difference(program.variables)

        return program

    def __get_all_variables__(self, assignments):
        return [a.variable for a in assignments]

    def __get_all_symbols__(self, assignments):
        all_symbols = set()
        for assign in assignments:
            all_symbols |= assign.get_free_symbols()
        return all_symbols

