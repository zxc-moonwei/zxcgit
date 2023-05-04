# 管理.zxcgit 目录里面的数据

import os
import hashlib

GIT_DIR = '.zxcgit'


def init():
    os.makedirs(GIT_DIR, exist_ok=True)


def hash_object(data):
    oid = hashlib.sha1(data).hexdigest()  # 转16进制
    path = os.path.join(GIT_DIR, "objects", oid)
    # os.path.dirname用于返回文件在的目录，如果目录已经存在，
    # 由于exist_ok参数设置为True，不会引发错误。
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as out:
        out.write(data)
    return oid

