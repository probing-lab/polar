class Graph:
    """
    Responsible for storing program variable dependencies graph.
    """

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

    def __dfs__(self, v, mark):
        mark[v] = True
        for i in range(self.V):
            if (self.adj[v][i] > 0) and (not mark[i]):
                self.__dfs__(i, mark)

    def get_bad_nodes(self):
        """
        Responsible for detecting bad variables in dependency graph. A variable is bad iff
        1. It appears on a cycle with at least one non-linear dependency typed edge.
        2. Is reachable from any vertex of any cycle described above.
        """
        bad = [False] * self.V
        for v in range(self.V):
            for u in range(self.V):
                if v == u:
                    if self.adj[v][u] == 2:
                        mark = [False] * self.V
                        self.__dfs__(v, mark)
                        for i in range(self.V):
                            if mark[i]:
                                bad[i] = True
                    continue
                if self.adj[v][u] == 2:
                    mark = [False] * self.V
                    self.__dfs__(u, mark)
                    if mark[v]:
                        mark = [False] * self.V
                        self.__dfs__(v, mark)
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
