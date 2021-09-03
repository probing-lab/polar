from typing import Dict
from symengine.lib.symengine_wrapper import Expr


class CornishFisherExpansion:

    cumulants: Dict[int, Expr]

    def __init__(self, cumulants: Dict[int, Expr]):
        self.cumulants = cumulants

    def __call__(self):
        # TODO: implement
        pass
