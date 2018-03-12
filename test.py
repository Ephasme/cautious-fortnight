from config_tools import load_config, build_graph, create_index_from_config
from utils import dump_object, print_object
from index import diff_trees
from graph import depth_first_search, find_roots
import json

# index1 = create_index_from_config(".apps/alcuin1.json")
index1 = create_index_from_config(".apps/MDC_ENSSUP_EVO.json")

# index2 = create_index_from_config(".apps/alcuin1_other.json")
index2 = create_index_from_config(".apps/MODULE_ENSSUP.json")

(id1, t1) = index1.write_tree()
(id2, t2) = index2.write_tree()

t = dict(t1, **t2)
dump_object("trees.json", t)
dump_object('i1.json', dict(index1.blobs, **index2.blobs))

def visitor(*args):
    print(args)

diff_trees(visitor, id1, id2, t)
