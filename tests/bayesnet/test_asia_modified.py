from __future__ import annotations
import os
import unittest

from bayesnet.parser import BifParser
from bayesnet.bayes_network import BayesNetwork
from bayesnet.bayes_variable import BayesVariable

ASIA_PATH = os.path.dirname(os.path.abspath(__file__)) + "/positive/asia_modified.bif"

correct_network: BayesNetwork = BayesNetwork("unknown", ["version 2.0", "author ProbingLab"], 0.001)

asia_visit: BayesVariable = BayesVariable("asia_visit", ("has-visited", "no-visit"), ["this-is-a-property"])
asia_visit.parents = ()
asia_visit.cpt = {(): (0.01, 0.99)}

tuber: BayesVariable = BayesVariable("tub-er", ("yes", "no"), [])
tuber.parents = (asia_visit,)
tuber.cpt = {("has-visited",): (0.05, 0.95), ("no-visit",): (0.01, 0.99)}

smoke: BayesVariable = BayesVariable("smoke", ("yes", "no"), [])
smoke.parents = ()
smoke.cpt = {(): (0.5, 0.5)}

lung: BayesVariable = BayesVariable("lung", ("yes", "no"), [])
lung.parents = (smoke,)
lung.cpt = {("yes",): (0.1, 0.9), ("no",): (0.01, 0.99)}

bronc: BayesVariable = BayesVariable("bronc", ("yes", "no"), [])
bronc.parents = (smoke,)
bronc.cpt = {("yes",): (0.6, 0.4), ("no",): (0.3, 0.7)}

either: BayesVariable = BayesVariable("either", ("yes", "no"), [])
either.parents = (lung, tuber)
either.cpt = {
    ("yes", "yes"): (1.0, 0.0), ("yes", "no"): (1.0, 0.0),
    ("no", "yes"): (1.0, 0.0), ("no", "no"): (0.0, 1.0)
}

dysp: BayesVariable = BayesVariable("dysp", ("yes", "no"), [])
dysp.parents = (bronc, either)
dysp.cpt = {
    ("yes", "yes"): (0.9, 0.1), ("yes", "no"): (0.8, 0.2),
    ("no", "yes"): (0.7, 0.3), ("no", "no"): (0.1, 0.9)
}

variables = [asia_visit, tuber, smoke, lung, bronc, either, dysp]
for v in variables:
    v.network = correct_network
    correct_network.add_variable(v)


class AsiaModifiedTest(unittest.TestCase):
    def test_asia_modified(self: AsiaModifiedTest):
        network = BifParser().parse_file(ASIA_PATH)
        self.assertEqual(correct_network, network)
        return


if __name__ == '__main__':
    unittest.main()
