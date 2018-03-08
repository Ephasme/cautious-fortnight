import json
from repository import Index
from itertools import groupby

def walk_tree(task, value, path = []):
    stack = [(value, path)]
    while stack:
        (cur_value, cur_path) = stack.pop()
        if isinstance(cur_value, dict):
            for attr, val in cur_value.items():
                stack.append((val, [*cur_path, attr]))
        elif isinstance(cur_value, list):
            for idx, val in enumerate(cur_value):
                stack.append((val, [*cur_path, str(idx)]))
        else:
            task(cur_value, cur_path)

def load_json_export(file):
    def remove_key_from_dict(item, key):
        r = dict(item)
        del r[key]
        return r

    def remove_key_from_many_dicts(items, key):
        return [remove_key_from_dict(item, key) for item in list(items)]

    def group_by_type(items):
        key_value = "ObjectType"
        key_selector = lambda x:x[key_value]
        sorted_list = sorted(items, key=key_selector)
        return {k: remove_key_from_many_dicts(v, key_value) for k, v in groupby(sorted_list, key_selector)}
    
    def group_by_id(items):
        return {v["Id"]: remove_key_from_dict(v, "Id") for v in items}

    with open(file, 'r', encoding='utf8', errors='strict') as json_file:
        obj = json.load(json_file)
        obj = group_by_type(obj["Content"]["Added"])
        return {k: group_by_id(v) for k, v in obj.items()}

def create_index_from_json_export(export_file):
    content = load_json_export(export_file)
    index = Index()
    def add_index(value, path):
        index.add('/'.join(path), value)
    walk_tree(add_index, content, [])
    return index

