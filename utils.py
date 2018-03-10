import json
import zlib
from hashlib import sha1

def hash_object(obj):
    return sha1(str(obj).encode()).hexdigest()

def load_object(filename):
    with open(filename, 'rb') as fsock:
        return json.loads(zlib.decompress(fsock.read()), encoding='utf8')

def save_object(filename, obj):
    with open(filename, 'wb') as fsock:
        fsock.write(zlib.compress(json.dumps(obj, ensure_ascii=False).encode('utf8')))

def dump_object(filename, obj):
    with open(filename, 'w', encoding='utf8', errors='strict') as fsock:
        fsock.write(json.dumps(obj, indent=2, ensure_ascii=False))

def print_object(obj):
    print(json.dumps(obj, indent=2, ensure_ascii=False))
