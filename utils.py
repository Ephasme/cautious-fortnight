import json
import zlib

def _default(obj):
    if isinstance(obj, set):
        return list(obj)
    else:
        raise TypeError

def load_object(filename):
    with open(filename, 'rb') as fsock:
        return json.loads(zlib.decompress(fsock.read()), encoding='utf8')

def save_object(filename, obj):
    with open(filename, 'wb') as fsock:
        fsock.write(zlib.compress(json.dumps(obj, ensure_ascii=False, default=_default).encode('utf8')))

def dump_object(filename, obj):
    with open(filename, 'w', encoding='utf8', errors='strict') as fsock:
        fsock.write(json.dumps(obj, indent=2, ensure_ascii=False, default=_default))

def print_object(obj):
    print(json.dumps(obj, indent=2, ensure_ascii=False, default=_default))
