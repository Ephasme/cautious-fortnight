from crypto import sha1

class Multimap(dict):
    def __missing__(self, key):
        arr = set()
        self[key] = arr
        return arr

class Graph:
    def __init__(self, nodes, refs):
        self.nodes = nodes
        self.children = refs
        self.parents = Multimap()
        for o_id, o_refs in self.children.items():
            for o_ref in o_refs:
                self.parents[o_ref].add(o_id)
    
    def __str__(self):
        return f"nodes: {self.nodes}\nrefs: {self.children}"

    def has_parents(self, node_id):
        return node_id in self.parents

    def has_children(self, node_id):
        return node_id in self.children

    def roots(self):
        return {x: self.nodes[x] for x, y in self.children.items() if not y and x in self.nodes}
    
    def leafs(self):
        return {x: self.nodes[x] for x in self.children if not x in self.parents and x in self.nodes}

    def exists(self, node_id):
        return node_id in self.nodes

    def neighbours_of(self, node_id):
        return set(self.children_of(node_id)) | set(self.parents_of(node_id))

    def children_of(self, node_id):
        return filter(self.exists, self.children[node_id])

    def parents_of(self, node_id):
        return filter(self.exists, self.parents[node_id])

def find_roots(graph):
    visited = set()
    degrees = {}
    for node in list(graph.nodes):
        if not node in visited:
            sub_graph = list(depth_first_search(graph, node, True))
            (node, _, degree) = max(sub_graph, key=lambda x: x[2])
            degrees[node] = max(degrees.get(node, 0), degree)
            visited |= set([c for (c, p, d) in sub_graph])
    return degrees.keys()


def depth_first_search(graph, starting_node, reverse=False):
    stack = [(starting_node, [], 0)]
    visited = set()
    while stack:
        (current, path, degree) = stack.pop()
        yield (current, path, degree)
        visited.add(current)
        if reverse:
            select_next_nodes = graph.parents_of
        else:
            select_next_nodes = graph.children_of
        for child in select_next_nodes(current):
            if not child in visited:
                stack.append((child, [*path, current], degree+1))

def strongly_connected_components(graph, visit):
    indexes = {}
    low_links = {}
    on_stack = {node: False for node in graph.nodes}
    stack = []
    
    def _get_component(current_node, index, path=[]):
        indexes[current_node] = index
        low_links[current_node] = index
        index += 1
        stack.append(current_node)
        on_stack[current_node] = True

        for next_node in graph.children_of(current_node):
            if not next_node in indexes:
                _get_component(next_node, index, [*path, current_node])
                low_links[current_node] = min(low_links[current_node], low_links[next_node])
            elif on_stack[next_node]:
                low_links[current_node] = min(low_links[current_node], indexes[next_node])

        if low_links[current_node] == indexes[current_node]:

            scc = []

            while True:
                node = stack.pop()
                on_stack[node] = False
                scc.append(node)
                if node == current_node:
                    break
            
            visit(path, scc)

    for v in graph.nodes:
        if not v in indexes:
            _get_component(v, 0, [])
