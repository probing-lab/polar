from argparse import Namespace
from bayesnet.parser import BifParser
from bayesnet.code_generator import CodeGenerator
from bayesnet.query.sampling_time_query import SamplingTimeQuery
from bayesnet.query.exact_inference_query import ExactInferenceQuery
from cli.argument_parser import ArgumentParser
from inputparser import GoalParser
from inputparser.goal_parser import MOMENT
from inputparser.parser import Parser
from recurrences.rec_builder import RecBuilder
from .action import Action
from program import Program
from cli.common import prepare_program, get_moment, parse_program


class BayesNetworkAction(Action):
    cli_args: Namespace
    program: Program

    def __init__(self, cli_args: Namespace):
        self.cli_args = cli_args

    def __call__(self, *args, **kwargs):
        benchmark = args[0]
        network = BifParser().parse_file(benchmark)
        print(network.print_pretty())

        if self.cli_args.sample_time_until is not None:
            query = SamplingTimeQuery(self.cli_args.sample_time_until, network)
        elif self.cli_args.exact_inference is not None:
            query = ExactInferenceQuery(self.cli_args.exact_inference, network)

        codegen = CodeGenerator(network, query)
        code = codegen.generate_code()
        print(code)
        program = Parser().parse_string(code, self.cli_args.transform_categoricals)
        goal_queries = query.generate_query(network, codegen.polar_variable_names)

        cli_args = ArgumentParser().get_defaults()
        program = prepare_program(program, cli_args)
        rec_builder = RecBuilder(program)

        parsed_queries = [GoalParser.parse(goal) for goal in goal_queries]
        results = []
        for goal_type, goal_data in parsed_queries:
            assert goal_type == MOMENT
            monom = goal_data[0]
            result, is_exact = get_moment(monom, {}, rec_builder, cli_args, program)
            results.append(result)

        query.generate_result(results)
