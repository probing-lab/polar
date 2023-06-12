from typing import Set, Tuple
from symengine.lib.symengine_wrapper import Symbol as SymengineSymbol

SymbolSet = Set[SymengineSymbol]


class Graph:
    """
    Responsible for storing program variable dependencies graph.
    """

    # Implementation Detail: the field self.adj is 2 if an edge is non-linear and 1 if it is linear

    def __init__(self, variables_cnt):
        self.adj = [[0] * variables_cnt for i in range(variables_cnt)]
        self.nodes = {}
        self.V = 0

    def add_node(self, v):
        if v in self.nodes:
            return
        else:
            self.nodes[v] = self.V
            self.V += 1

    def add_edge(self, v, u, e):
        v, u = u, v
        v, u = self.nodes[v], self.nodes[u]
        if e > self.adj[v][u]:
            self.adj[v][u] = e

    def __repr__(self):
        res = ""
        for i in range(self.V):
            for j in range(self.V):
                res += str(self.adj[i][j])
            res += "\n"
        return res

    def _dfs(self, v, mark):
        mark[v] = True
        for i in range(self.V):
            if (self.adj[v][i] > 0) and (not mark[i]):
                self._dfs(i, mark)

    def get_reachable_variables(self, variable: SymengineSymbol) -> SymbolSet:
        """
        Get all variables reachable from some other variable in the dependency graph
        """
        mark = [False] * self.V
        node = self.nodes[variable]
        self._dfs(node, mark)

        # reconstruct reachable vars from array
        result = set()
        for i in range(self.V):
            if mark[i]:
                for var in self.nodes.keys():
                    if self.nodes[var] == i:
                        result.add(var)
                        break
        return result

    def is_variable_in_nonlinear_cycle(self, v: SymengineSymbol) -> bool:
        """
        Check if a variable is part of a non-linear cycle.
        """
        v_idx = self.nodes[v]
        # iterate over all non-linear edges:
        for start in range(self.V):
            for end in range(self.V):
                if self.adj[start][end] == 2:
                    # in case of NL self-dependency -> done
                    if start == end and start == v_idx:
                        return True

                    # v is part of a NL-cycle <=>
                    #   it can reach the starting point of a NL edge and the endpoint of the edge can reach v

                    # check if variable is reachable from endpoint of NL-edge
                    mark = [False] * self.V
                    self._dfs(end, mark)
                    if mark[v_idx] is False:
                        continue

                    # check if variable can reach other endpoint of NL-edge
                    mark = [False] * self.V
                    self._dfs(v_idx, mark)
                    if mark[start]:
                        return True
        return False

    def get_defective_nodes(self):
        """
        Responsible for detecting defective variables in dependency graph. A variable is defective iff
        1. It appears on a cycle with at least one non-linear dependency typed edge.
        2. Is reachable from any vertex of any cycle described above.
        """
        bad = [False] * self.V
        for v in range(self.V):
            for u in range(self.V):
                if v == u:
                    if self.adj[v][u] == 2:
                        mark = [False] * self.V
                        self._dfs(v, mark)
                        for i in range(self.V):
                            if mark[i]:
                                bad[i] = True
                    continue
                if self.adj[v][u] == 2:
                    mark = [False] * self.V
                    self._dfs(u, mark)
                    if mark[v]:
                        mark = [False] * self.V
                        self._dfs(v, mark)
                        for i in range(self.V):
                            if mark[i]:
                                bad[i] = True

        result = set()
        for i in range(self.V):
            if bad[i]:
                for u in self.nodes.keys():
                    if self.nodes[u] == i:
                        result.add(u)
        return result
