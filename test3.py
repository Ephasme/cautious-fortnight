from config_tools import load_config, build_graph, create_index_from_config
from utils import dump_object, print_object
from index import diff_trees
from graph import connected_components, depth_first_search, find_roots
import json

# g = build_graph(load_config('.apps/MDC_ENSSUP_EVO.json'))

# print(list(depth_first_search(g, "00004", True)))

index1 = create_index_from_config(".apps/alcuin1.json")
print(index1)
# index1 = create_index_from_config(".apps/MDC_ENSSUP_EVO.json")

# index2 = create_index_from_config(".apps/alcuin1_other.json")
# index2 = create_index_from_config(".apps/MDC_ENSSUP_EVO.json")

# (id1, t1) = index1.write_tree()
# print(id1, json.dumps(t1, indent=2))
# (id2, t2) = index2.write_tree()

# t = dict(t1, **t2)

# def visitor(*args):
#     print(args)

# diff_trees(visitor, id1, id2, t)
