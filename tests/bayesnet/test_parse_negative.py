import glob
import os
import unittest

from bayesnet.parser import BifParser
from bayesnet.exceptions import BifFormatException

NEGATIVES_PATH = os.path.dirname(os.path.abspath(__file__)) + "/negative"


def create_neg_parse_test(file: str):
    def test(self: NegParseFileTest):
        self.assertRaises(BifFormatException, BifParser().parse_file, file)

    return test


class NegParseFileTest(unittest.TestCase):
    """Checks if parser correctly rejects the given file."""

    pass


negatives = glob.glob(NEGATIVES_PATH + "/*")
for negative in negatives:
    name = "test_" + os.path.basename(negative).replace(".bif", "")
    setattr(NegParseFileTest, name, create_neg_parse_test(negative))

if __name__ == "__main__":
    unittest.main()
