import json
from index import Index
from utils import print_object

def is_ref(d: dict):
    return 'TargetId' in d and 'IsRef' in d and d['IsRef']

def add_index(index):
    def _inner(value, path):
        index.add('/'.join(path), value)
    return _inner

def walk_tree(task, registry, value, path = []):
    stack = [(value, path)]
    while stack:
        (cur_value, cur_path) = stack.pop()
        if isinstance(cur_value, dict):
            if is_ref(cur_value):
                target_id = cur_value['TargetId']
                target = registry[target_id]
                stack.append((target, [*cur_path, target_id]))
            else:
                for attr, val in cur_value.items():
                    stack.append((val, [*cur_path, attr]))
        elif isinstance(cur_value, list):
            for idx, val in enumerate(cur_value):
                stack.append((val, [*cur_path, str(idx)]))
        else:
            task(cur_value, cur_path)

with open('.apps/alcuin1.json', 'r', encoding='utf8') as fs:
    config_file = json.load(fs)
    registry = {item.pop('Id'): item for item in config_file["Content"]["Added"]}

    index = Index()
    walk_tree(add_index(index), registry, registry)

    tree = index.write_tree()
    print_object(tree)
    print(index)
