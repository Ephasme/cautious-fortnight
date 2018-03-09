import json
from hashlib import sha1
from posixpath import normpath, split
from itertools import groupby
from datetime import datetime
import os
import zlib

def _key_selector(t):
    return t[0][0]

def _drop_key(t):
    return (t[0][1:], t[1])

def _group_by_first(items: list):
    sort = list(sorted(items, key=_key_selector))
    for k, v in groupby(sort, key=_key_selector):
        yield (k, map(_drop_key, v))

def _hash_tree(tree):
    tree_index = {}

    def _recursor(cur_tree):
        cur_tree = list(cur_tree)

        blobs = [t for t in cur_tree if len(t[0]) == 1]
        subtrees = [t for t in cur_tree if len(t[0]) > 1]

        content = [(t[0][0], 'blob', t[1]) for t in blobs]

        for k, v in _group_by_first(subtrees):
            content.append((k, 'tree', _recursor(v)))

        id_content = hash_object(content)
        tree_index[id_content] = content
        return id_content

    return (_recursor(tree), tree_index)

def hash_object(obj):
    return sha1(str(obj).encode()).hexdigest()

def load_file(filename):
    with open(filename, 'rb') as fsock:
        return json.loads(zlib.decompress(fsock.read()), encoding='utf8')

def dump_object(filename, obj):
    with open(filename, 'w', encoding='utf8', errors='strict') as fsock:
        fsock.write(json.dumps(obj, indent=4, ensure_ascii=False))

def dump_index(filename, index):
    dump_object(filename, {
        'paths': index.paths,
        'blobs': index.blobs
    })

def walk_tree(trees_index, root_id, task):
    stack = [(root_id, [])]
    
    def __path_str(path):
        return '/'.join(path)

    while stack:
        (node_id, path) = stack.pop()
        node = trees_index[node_id]
        for path_segment, type, ref in node:
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

def save_file(filename, obj):
    with open(filename, 'wb') as fsock:
        fsock.write(zlib.compress(json.dumps(obj, ensure_ascii=False).encode('utf8')))

def load_index(index_file):
    index = Index()
    data = load_file(index_file)
    index.paths = data['paths']
    index.blobs = data['blobs']
    return index

def save_index(index_file, index):
    save_file(index_file, {
        'paths': index.paths,
        'blobs': index.blobs
    })

def load_repository():
    repo = Repository()
    os.makedirs('.repo', exist_ok=True)
    repo.trees = load_file('./repo/trees')
    repo.commits = load_file('./repo/commits')
    repo.index = load_index('./repo/index')
    return repo

def save_repository(repository):
    save_file('./repo/trees', repository.trees)
    save_file('./repo/commits', repository.commits)
    save_index('./repo/index', repository.index)

def diff_trees(tree_id_a, tree_id_b, trees, path=[]):
    print(f'at {"/".join(path)}')

    root_a = trees.get(tree_id_a)
    root_b = trees.get(tree_id_b)

    common_keys = set(root_a.keys()) | set(root_b.keys())

    for key in common_keys:
        new_path = [*path, key]
        new_path_str = '/'.join(new_path)

        a = root_a.get(key)
        b = root_b.get(key)
        
        if a and b and a[0] == 'tree' and a[1] == b[1]:
            print(f"everything in {new_path_str} is ok")
        if a and b and a[0] == 'tree' and a[1] != b[1]:
            print(f"go to => {new_path_str}")
            diff_trees(a[1], b[1], trees, new_path)
        if a and b and a[0] == 'blob' and a[1] != b[1]:
            print(f"{new_path_str}: {a[1]} vs {b[1]}")
        if a and not b:
            print(f"{a[0]} {new_path_str} only exists in a")
        if b and not a:
            print(f"{b[0]} {new_path_str} only exists in b")

class Index:
    def __init__(self):
        self.paths = {}
        self.blobs = {}
        self.ROOT_NAME = 'r'

    def add(self, path, value):
        def __create_blob_id():
            id = hash_object(value)
            self.blobs[id] = value
            return id        
        path = normpath(self.ROOT_NAME + '/' + path)
        blob_id = __create_blob_id()
        self.paths[path] = blob_id

    def write_tree(self):
        return _hash_tree([(path.split('/'), blob_id) for path, blob_id in self.paths.items()])

    def rm(self, path):
        path = normpath(self.ROOT_NAME + '/' + path)
        del self.paths[path]        

class Repository:
    def __init__(self):
        self.trees = {}
        self.commits = {}
        self.index = Index()
    
    def write_tree(self):
        (tree_id, tree) = self.index.write_tree()
        self.trees = dict(self.trees, **tree)
        return tree_id

    def write_commit(self, message, author, tree_id, previous=[]):
        commit = {
            'tree_id': tree_id,
            'previous': previous,
            'message': message,
            'date': datetime.now().__str__(),
            'author': author
        }
        id = hash_object(commit)
        self.commits[id] = commit
        return id

    # def diff_commits(self, commit_id1, commit_id2):
    #     c1 = self.commits[commit_id1]
    #     c2 = self.commits[commit_id2]
    #     return self.diff_trees(c1['tree_id'], c2['tree_id'])
