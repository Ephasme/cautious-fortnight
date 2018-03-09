import json
import argparse
import time
import convert_utils as utils
from repository import (
    dump_index,
    dump_object,
    build_index_from_tree,
    diff_trees,
    walk_tree
)
from convert_utils import create_index_from_json_export

index1 = create_index_from_json_export('alcuin1.json')
index2 = create_index_from_json_export('alcuin1_other.json')

(tree_id_1, tree_1) = index1.write_tree()
(tree_id_2, tree_2) = index2.write_tree()

trees = dict(tree_1, **tree_2)

diff_trees(tree_id_1, tree_id_2, trees)