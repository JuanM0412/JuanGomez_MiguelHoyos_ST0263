import hashlib


def get_hash(key):
    result = hashlib.sha1(key.encode())
    return int(result.hexdigest(), 16) % 128