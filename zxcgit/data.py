# 管理.zxcgit 目录里面的数据

import os
import hashlib

GIT_DIR = '.zxcgit'


def init():
    os.makedirs(GIT_DIR, exist_ok=True)


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


def update_ref(ref, oid):
    path = os.path.join(GIT_DIR, ref)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(oid)


def get_ref(ref):
    # 第一次get_ref会返回None
    path = os.path.join(GIT_DIR, ref)
    if os.path.isfile(path):
        with open(path, "r") as f:
            return f.read()
