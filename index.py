from utils import (
    dump_object, 
    save_object, 
)
from crypto import sha1
import json
from itertools import groupby
from posixpath import normpath

def _key_selector(t):
    return t[0][0]

def _drop_key(t):
    return (t[0][1:], t[1])

def _group_by_first(items: list):
    sort = list(sorted(items, key=_key_selector))
    for k, v in groupby(sort, key=_key_selector):
        yield (k, map(_drop_key, v))

def hash_tree(tree):
    tree_index = {}

    def _recursor(cur_tree):
        cur_tree = list(cur_tree)
        
        subtrees = {k: ('tree', _recursor(v)) for k, v in _group_by_first([t for t in cur_tree if len(t[0]) > 1])}
        blobs = {t[0][0]: ('blob', t[1]) for t in [t for t in cur_tree if len(t[0]) == 1]}

        content = dict(**subtrees, **blobs)

        id_content = sha1(content)
        tree_index[id_content] = content
        return id_content

    return (_recursor(tree), tree_index)

def walk_tree(trees_index, root_id, task):
    stack = [(root_id, [])]
    
    def __path_str(path):
        return '/'.join(path)

    while stack:
        (node_id, path) = stack.pop()
        node = trees_index[node_id]
        for path_segment, (type, ref) in node.items():
            new_path = [*path, path_segment]
            if type == 'tree':
                stack.append((ref, new_path))
            else:
                task(ref, new_path)

def build_index_from_tree(trees_index, blobs, root_id):
    index = Index()
    def __task(blob_id, path):
        index.add('/'.join(path), blobs[blob_id])
    walk_tree(trees_index, root_id, __task)
    return index

def diff_trees(visitor, tree_id_a, tree_id_b, trees, path=[]):
    root_a = trees.get(tree_id_a)
    root_b = trees.get(tree_id_b)

    common_keys = set(root_a.keys()) | set(root_b.keys())

    for key in common_keys:
        new_path = [*path, key]

        a = root_a.get(key)
        b = root_b.get(key)
        
        if a and b and a[0] == 'tree' and a[1] != b[1]:
            diff_trees(visitor, a[1], b[1], trees, new_path)
        elif a and b and a[0] == 'blob' and a[1] != b[1]:
            visitor(new_path, 'conflict', a[1], b[1])
        elif a and not b:
            visitor(new_path, 'deleted')
        elif b and not a:
            visitor(new_path, 'created')

class Index:
    def __init__(self):
        self.paths = {}
        self.blobs = {}

    def pack(self):
        return {
            'paths': self.paths,
            'blobs': self.blobs
        }

    def dump(self, filename):
        dump_object(filename, self.pack())

    def save(self, filename):
        save_object(filename, self.pack())

    def __str__(self):
        def _set_default(obj):
            if isinstance(obj, set):
                return list(obj)
            raise TypeError
        return json.dumps(self.pack(), indent=2,
            ensure_ascii=False, default=_set_default)

    def add(self, path, value):
        def __create_blob_id():
            hash_id = sha1(value)
            self.blobs[hash_id] = value
            return hash_id        
        path = normpath(path)
        blob_id = __create_blob_id()
        self.paths[path] = blob_id

    def write_tree(self):
        return hash_tree([(path.split('/'), blob_id) for path, blob_id in self.paths.items()])

    def rm(self, path):
        path = normpath(path)
        del self.paths[path] 