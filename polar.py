#!/usr/bin/env python3

"""This file is part of Polar

This runnable script allows the user to run Polar on probabilistic programs stored in files
For the command line arguments run the script with "--help".
"""
import time
from cli import logo, ArgumentParser
from cli.actions import ActionFactory
from termcolor import colored


def main():
    print(colored(logo, "green"))
    print()
    print()

    start = time.time()
    args = ArgumentParser().parse_args()

    try:
        action = ActionFactory.create_action(args)
        for benchmark in args.benchmarks:
            action(benchmark)
    except Exception as e:
        raise e
        print(e)
        exit()

    print(f"Elapsed time: {time.time() - start} s")


if __name__ == "__main__":
    main()
