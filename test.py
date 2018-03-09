import json
import argparse
import time
import convert_utils as utils
from repository import (
    dump_index,
    dump_object,
    build_index_from_tree
)
from convert_utils import create_index_from_json_export

index1 = create_index_from_json_export('alcuin1.json')
index2 = create_index_from_json_export('alcuin1_other.json')

(tree_id_1, tree_1) = index1.write_tree()
dump_object('tree1-dump.json', tree_1)

(tree_id_2, tree_2) = index2.write_tree()

dump_index('index.json', index1)
dump_index('generated-index.json', build_index_from_tree(tree_1, index1.blobs, tree_id_1))

trees = dict(tree_1, **tree_2)
