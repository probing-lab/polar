import itertools

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
        print("ADD_EDGE {} {} {}".format(v, u, e))
        assert (v in self.nodes) and (u in self.nodes), "NODES NOT ADDED"
        v, u = self.nodes[v], self.nodes[u]
        if e > self.adj[v][u]:  # polynomial dependency found after than linear dependency --> replace it
            self.adj[v][u] = e

    def __repr__(self):
        res = ""
        for i in range(self.V):
            for j in range(self.V):
                res += str(self.adj[i][j])
            res += "\n"

        return res

    def __get_all_possible_cycles(self):
        result = []
        ps = []  # powerset of {0, 1, ..., self.V - 1}
        for i in range(2 ** self.V):
            cur = []
            for j in range(self.V):
                if (i & (1 << j)) > 0:
                    cur.append(j)
            ps.append(cur)

        for s in ps:
            cur = list(itertools.permutations(s))
            for perm in cur:
                result.append(list(perm))

        return result

    def get_bad_nodes(self):  # all nodes appearing in a cycle with a least on type 2 edge
        bad = set()
        candidate = self.__get_all_possible_cycles()

        for cand in candidate:
            has_non_linear_edge = False
            cycle = True

            if len(cand) == 1:
                if self.adj[cand[0]][cand[0]] == 2:
                    print("Found cycle {}".format(cand))
                    print("Bad cycle detected!")
                    bad.add(cand[0])
                continue

            for i in range(len(cand) - 1):
                v = cand[i]
                u = cand[i + 1]
                if self.adj[v][u] == 0:
                    cycle = False
                    break
                if self.adj[v][u] == 2:
                    has_non_linear_edge = True

            if len(cand) > 1:
                if self.adj[cand[-1]][cand[0]] == 0:
                    cycle = False

            if cycle:
                print("Found cycle {}".format(cand))
            if cycle and has_non_linear_edge:
                print("Bad cycle detected!")
                for v in cand:
                    bad.add(v)

        result = []
        for v in bad:
            for u in self.nodes.keys():
                if self.nodes[u] == v:
                    result.append(u)

        return result


if __name__ == '__main__':
    g = Graph()
    g.add_node("a")
    g.add_node("b")
    g.add_node("c")
    g.add_node("d")
    # g.add_node("e")
    # g.add_node("f")
    # g.add_node("g")
    g.add_node("h")
    g.add_node("i")
    g.add_node("j")

    print(g.nodes)
    print()

    g.add_edge("a", "b", 1)
    g.add_edge("b", "c", 2)
    g.add_edge("c", "d", 1)
    g.add_edge("a", "d", 1)

    # g.add_edge("e", "f", 1)
    # g.add_edge("f", "g", 2)
    # g.add_edge("g", "e", 1)

    g.add_edge("d", "i", 1)
    g.add_edge("i", "h", 1)
    g.add_edge("h", "d", 1)

    g.add_edge("i", "j", 2)
    g.add_edge("j", "i", 2)

    print(g)
    print()

    print(g.get_bad_nodes())
