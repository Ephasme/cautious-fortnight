from hashlib import sha1 as _sha1
from json import dumps

def sha1(obj):
    return _sha1(dumps(obj, ensure_ascii=False).encode('utf8')).hexdigest()
