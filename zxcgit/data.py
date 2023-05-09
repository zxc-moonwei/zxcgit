# 管理.zxcgit 目录里面的数据

import os
import hashlib
from collections import namedtuple

GIT_DIR = '.zxcgit'


def init():
    os.makedirs(GIT_DIR, exist_ok=True)


# 传来一个data
# 在.zxcgit/object下建立blob object,tree object等hash object
def hash_object(data, type_='blob'):
    # 将type拼接到data前面
    obj = type_.encode() + b'\x00' + data
    oid = hashlib.sha1(obj).hexdigest()  # 转16进制
    path = os.path.join(GIT_DIR, "objects", oid)
    # os.path.dirname用于返回文件在的目录，如果目录已经存在，由于exist_ok参数设置为True，不会引发错误。
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as out:
        out.write(obj)
    return oid


def get_object(oid, expect=None):
    path = os.path.join(GIT_DIR, "objects", oid)
    with open(path, "rb") as f:
        obj = f.read()
    type_, _, data = obj.partition(b"\x00")
    type_ = type_.decode()
    if expect is not None:
        assert expect == type_, f"TypeError!Expect {expect},but got {type_}"
    return data


RefValue = namedtuple('RefValue', ['symbolic', 'value'])


def update_ref(ref, ref_value, deref=True):
    # 把符号链处理掉真正指向oid的ref
    ref = _get_ref_internal(ref, deref)
    path = os.path.join(GIT_DIR, ref)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(ref_value.value)


def get_ref(ref, deref):
    return _get_ref_internal(ref, deref)[1]


# 传来ref在.zxcgit下的实际路径
# 如果是符号链，检查deref , 如果确定解引用
# 输出真正指向oid的ref_name, RefValue(symbolic,value)
# 否则直接输出ref_name和引用内容
def _get_ref_internal(ref, deref):
    # 第一次get_ref会返回None
    path = os.path.join(GIT_DIR, ref)
    value = None
    if os.path.isfile(path):
        with open(path, "r") as f:
            value = f.read()
    symbolic = bool(value) and value.startswith('ref:')
    if symbolic and deref:
        return _get_ref_internal(value.split(':', 1)[1].strip(), deref=True)
    return ref, RefValue(symbolic=symbolic, value=value)


# 遍历.zxcgit/refs所有的ref
# 返回生成器ref_name,ref指向的oid
def iter_ref(deref=True):
    res = ['HEAD']
    # ref_name为ref/下所有filename，以ref为root,或者为‘HEAD’
    for root, _, filenames in os.walk(os.path.join(GIT_DIR, "refs")):
        root = os.path.relpath(root, GIT_DIR)
        res.extend(os.path.join(root, c) for c in filenames)
        # print(res)
    for ref in res:
        yield ref, get_ref(ref, deref)
