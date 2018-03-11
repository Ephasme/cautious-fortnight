import json
from datetime import datetime
from crypto import sha1
from utils import (
    dump_object,
    save_object,
)
from index import Index, diff_trees

class Repository:
    def __init__(self):
        self.trees = {}
        self.commits = {}
        self.index = Index()
        self.branches = {}
        self.head = None

    def pack(self):
        return {
            'index': self.index.pack(),

            'trees': self.trees,
            'commits': self.commits,
            'branches': self.branches,
            'head': self.head,
        }

    def dump(self, filename):
        dump_object(filename, self.pack())

    def save(self, filename):
        save_object(filename, self.pack())

    def __str__(self):
        return json.dumps(self.pack(), ensure_ascii=False)        

    def branch(self, name, ref):
        self.branches[name] = ref
    
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
        id = sha1(commit)
        self.commits[id] = commit
        return id

    def diff_branches(self, visitor, branch_a, branch_b):
        self.diff_commits(visitor, self.branches[branch_a], self.branches[branch_b])

    def diff_commits(self, visitor, ref_commit_a, ref_commit_b):
        commit_a = self.commits[ref_commit_a]
        commit_b = self.commits[ref_commit_b]
        return diff_trees(visitor, commit_a['tree_id'], commit_b['tree_id'], self.trees)
