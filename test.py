import time
from repository import Repository
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
index = create_index_from_config('MDC_ENSSUP_EVO.json')

repo = Repository()
repo.index = index

repo.save('MDC_ENSSUP_EVO.rep')

# index2 = create_index_from_json_export('MODULE_ENSSUP.json')

# (tree_id_1, tree_1) = index.write_tree()
# (tree_id_2, tree_2) = index2.write_tree()

# trees = dict(tree_1, **tree_2)
# blobs = dict(index.blobs, **index2.blobs)

# printer = PrinterVisitor(blobs)

# diff_trees(printer, tree_id_1, tree_id_2, trees)
