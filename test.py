import json
import argparse
from repository import (
    Repository, save_repository, load_repository,
    load_index, save_index, diff_trees, dump_object,
    dump_index, walk_tree, build_index_from_tree
)
from itertools import groupby
import time
import convert_utils as utils
from convert_utils import create_index_from_json_export




index1 = create_index_from_json_export('alcuin1.json')
print(list(index1.paths))

def build_graph(index):
    from posixpath import commonpath
    print(commonpath(list(index1.paths)))
    # groups_by_common_paths = groupby(index1.paths, key=commonprefix)
    # for key, val in groups_by_common_paths:
    #     print(key, list(val))
    # pass

build_graph(index1)

# index2 = create_index_from_json_export('alcuin1_other.json')

# (tree_id_1, tree_1) = index1.write_tree()
# dump_object('tree1-dump.json', tree_1)

# (tree_id_2, tree_2) = index2.write_tree()

# dump_index('index.json', index1)
# dump_index('generated-index.json', build_index_from_tree(tree_1, index1.blobs, tree_id_1))

# trees = dict(tree_1, **tree_2)

# walk_tree(trees, tree_id_1, lambda value, path: print(path, value))


# parser = argparse.ArgumentParser(description='JSON TOOL')

# subparser = parser.add_subparsers()

# update_index_parser = subparser.add_parser('update-index', help='update the repository index from a json configuration file')
# compile_index_parser = subparser.add_parser('write-index', help='write a json configuration file from an repository index')

# update_index_parser.add_argument('json-file', help='the source file')
# compile_index_parser.add_argument('json-file', help='the destination file')

# args = parser.parse_args()

# if args.update_index:
#     repo = load_repository()
#     print(repo.index.blobs)+