import itertools
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

    def __get_all_possible_cycles(self):
        result = []
        ps = []
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

    def dfs(self, v, mark):
        for i in range(self.V):
            if mark[i]:
                continue
            if self.adj[i][v]:
                mark[i] = True
                self.dfs(i, mark)

    def get_bad_nodes(self):
        bad = set()
        candidate = self.__get_all_possible_cycles()
        for cand in candidate:
            has_non_linear_edge = False
            cycle = True
            if len(cand) == 1:
                if self.adj[cand[0]][cand[0]] == 2:
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
                pass
            if cycle and has_non_linear_edge:
                for v in cand:
                    bad.add(v)
        mark = [False] * self.V
        for v in bad:
            mark[v] = True
        for v in bad:
            self.dfs(v, mark)
        for i in range(self.V):
            if mark[i]:
                bad.add(i)
        result = []
        for v in bad:
            for u in self.nodes.keys():
                if self.nodes[u] == v:
                    result.append(u)
        return set(result)


if __name__ == '__main__':
    g = Graph()
    g.add_node("a")
    g.add_node("b")
    g.add_node("c")
    g.add_node("d")

    g.add_node("h")
    g.add_node("i")
    g.add_node("j")

    print(g.nodes)
    print()

    g.add_edge("a", "b", 1)
    g.add_edge("b", "c", 2)
    g.add_edge("c", "d", 1)
    g.add_edge("a", "d", 1)

    g.add_edge("d", "i", 1)
    g.add_edge("i", "h", 1)
    g.add_edge("h", "d", 1)

    g.add_edge("i", "j", 2)
    g.add_edge("j", "i", 2)

    print(g)
    print()

    print(g.get_bad_nodes())
