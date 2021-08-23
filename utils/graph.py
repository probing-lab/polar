from program import Program

class Graph:

    def __init__(self, program: Program):
        self.adj = [[0] * len(program.variables) for i in range(len(program.variables))]
        self.nodes = {}
        self.V = 0

    def add_node(self, v):
        if v in self.nodes:
            return
        else:
            self.nodes[v] = self.V
            self.V += 1

    def add_edge(self, v, u, e):
        assert (v in self.nodes) and (u in self.nodes), "NODES NOT ADDED"
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


if __name__ == '__main__':
    g = Graph()
    g.add_node("a")
    g.add_node("b")
    g.add_node("c")
    g.add_node("d")
    g.add_node("e")
    g.add_node("f")

    print(g.nodes)
    print()

    g.add_edge("a", "b", 2)
    g.add_edge("b", "c", 1)
    g.add_edge("c", "d", 1)
    g.add_edge("d", "a", 1)

    g.add_edge("b", "e", 1)
    g.add_edge("f", "b", 1)

    print(g)
    print()

    print(g.get_bad_nodes())
