import json
from repository import Index
from itertools import groupby
from graph import Graph, find_roots

def load_config(filename):
    with open(filename, 'r', encoding='utf8') as fsock:
        return json.load(fsock)

def is_ref(d):
    try:
        return d['IsRef']
    except:
        return False

def visit_refs(obj, visitor):
    stack = [(obj, [])]
    while stack:
        (c, p) = stack.pop()
        if is_ref(c):
            yield visitor(c["TargetId"], p)
        elif isinstance(c, dict):
            stack.extend([(v, [*p, attr]) for attr, v in c.items()])

def find_guids(obj):
    return visit_refs(obj, lambda guid, _: guid)

def find_ref_paths(obj):
    return visit_refs(obj, lambda guid, path: (guid, path))

def build_graph(config: dict) -> Graph:
    refs = {obj['Id']: set(find_guids(obj)) for obj in config["Content"]["Added"]}
    nodes = {obj['Id']: obj for obj in config["Content"]["Added"]}
    return Graph(nodes, refs)

def __with_follow_symlinks(func):
    visited = set()
    def _wrapper(graph, cur_value, cur_path):
        if isinstance(cur_value, dict) and is_ref(cur_value):
            target_id = cur_value['TargetId']
            if not target_id in visited and target_id in graph.nodes:
                target = graph.nodes[target_id]
                visited.add(target_id)
                return [(target, [*cur_path, target_id])]
        else:
            return func(graph, cur_value, cur_path)
    return _wrapper

def __nodes_provider(graph, cur_value, cur_path):
    result = []
    if isinstance(cur_value, dict):
        for attr, val in cur_value.items():
            if attr != 'Id':
                result.append((val, [*cur_path, attr]))
    elif isinstance(cur_value, list):
        for idx, val in enumerate(cur_value):
            result.append((val, [*cur_path, str(idx)]))
    return result

def __ignore_targets(func):
    def _wrapper(graph, cur_value, cur_path):
        if isinstance(cur_value, dict) and is_ref(cur_value):
            return None
        else:
            return func(graph, cur_value, cur_path)
    return _wrapper

def __simplify_targets(walker):
    def _wrapper(cur_value, cur_path):
        if is_ref(cur_value):
            walker('@('+cur_value['TargetId']+')', cur_path)
        else:
            walker(cur_value, cur_path)
    return _wrapper

def __walk_config(walker, graph, stack, nodes_provider):
    while stack:
        (cur_value, cur_path) = stack.pop()
        next_nodes = nodes_provider(graph, cur_value, cur_path)
        if next_nodes:
            stack.extend(next_nodes)
        else:
            walker(cur_value, cur_path)

def walk_config(walker, config, follow_symlinks=False):
    graph = build_graph(config)
    if follow_symlinks:
        provider = __with_follow_symlinks(__nodes_provider)
        starting_nodes = [(graph.nodes[k], [k]) for k in find_roots(graph)]
    else:
        provider = __ignore_targets(__nodes_provider)
        walker = __simplify_targets(walker)
        starting_nodes = [(graph.nodes[k], [k]) for k in graph.nodes]
    __walk_config(walker, graph, starting_nodes, provider)

def create_index_from_config(config_file, follow_symlinks=False):
    index = Index()
    def add_index(value, path):
        index.add('/'.join(path), value)
    with open(config_file, 'r', encoding='utf8', errors='strict') as fsock:
        walk_config(add_index, json.load(fsock), follow_symlinks)
    return index
