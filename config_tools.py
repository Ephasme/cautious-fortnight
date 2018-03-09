import json
from repository import Index
from itertools import groupby

def _walk_tree(task, value, path = []):
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

def extract_guids(d, guids_list:list=[]):
    if (d == None or (not isinstance(d, dict) and not isinstance(d, list))):
        return guids_list
    try:
        if d['IsRef'] is True:
            return [d['TargetId']] + guids_list
    except (TypeError, KeyError) as e:
        pass
    
    new_guids_list = guids_list
    for prop in d:
        new_guids_list = extract_guids(d[prop] if isinstance(d, dict) else prop, new_guids_list)
    return new_guids_list

def load_config(file):
    def _build_graph(obj):
        pass

    def _to_index(obj):
        pass

    with open(file, 'r', encoding='utf8', errors='strict') as json_file:
        obj = json.load(json_file)['Content']['Added']
        _to_index(obj)
    return {}
    

def __old_load_config(file):
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

def create_index_from_config(export_file):
    content = load_config(export_file)
    index = Index()
    def add_index(value, path):
        index.add('/'.join(path), value)
    _walk_tree(add_index, content, [])
    return index

