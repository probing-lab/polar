MAX_NODES = 30

class Graph:

    def __init__(self):
        self.MAX_NODES = 20
        self.adj = [[0] * self.MAX_NODES for i in range(self.MAX_NODES)]
        self.nodes = {}  # hashing objects into numbers
        self.V = 0

    def add_node(self, v):
        if v in self.nodes:
            return
        else:
            self.nodes[v] = self.V
            self.V += 1

    def add_edge(self, v, u, e):  # v to u
        assert (v in self.nodes) and (u in self.nodes), "NODES NOT ADDED"
        v, u = self.nodes[v], self.nodes[u]
        if e > self.adj[v][u]:
            self.adj[v][u] = e

    def __repr__(self):
        res = ""
        for i in range(self.V):
            for j in range(self.V):
                res += str(self.adj[i][j])
            res += "\n"

        return str(self.adj)


if __name__ == '__main__':
    g = Graph()
    g.add_node("a")
    g.add_node("c")
    g.add_node("b")

    print(g.nodes)
    print()

    g.add_edge("a", "b", 1)
    print(g)
    print()

    g.add_edge("a", "c", 2)
    print(g)
    print()

    g.add_edge("a", "b", 2)
    print(g)
    print()

    print(g.nodes)
