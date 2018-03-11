import time
from index import diff_trees
from config_tools import create_index_from_config

class PrinterVisitor:
    def __init__(self, blobs):
        self.blobs = blobs
    def conflict(self, path, mine, theirs):
        print({'/'.join(path): (self.blobs[mine], self.blobs[theirs])})
    def deleted(self, path):
        print('deleted: ' + '/'.join(path))
    def created(self, path):
        print('created: ' + '/'.join(path))

start = time.time()
index = create_index_from_config('.apps/alcuin1.json')

(tree_id_1, tree_1) = index.write_tree()

index.add('TypeB/00002/1_LVL0_TREE_1/1_LVL1_BLOB_2', 'tagazok')
index.rm('TypeB/00002/1_LVL0_TREE_1/1_LVL1_BLOB_3')

(tree_id_2, tree_2) = index.write_tree()

trees = dict(tree_1, **tree_2)

printer = PrinterVisitor(index.blobs)

diff_trees(printer, tree_id_1, tree_id_2, trees)
