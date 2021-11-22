import glob
import os
import unittest

from bayesnet.parser import BifParser

POSITIVES_PATH = os.path.dirname(os.path.abspath(__file__)) + "/positive"


def create_parse_test(file: str):
    def test(self: ParseFileTest):
        network = BifParser().parse_file(file)
        self.assertIsNotNone(network)
    return test


class ParseFileTest(unittest.TestCase):
    """Checks if parser can parse the given file without errors."""
    pass


positives = glob.glob(POSITIVES_PATH + "/*")
for positive in positives:
    name = "test_" + os.path.basename(positive).replace(".bif", "")
    setattr(ParseFileTest, name, create_parse_test(positive))

if __name__ == '__main__':
    unittest.main()
