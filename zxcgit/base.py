"""
该模块将使用data模块提供的low-level功能，如对象存储，对象读取打印
来完成high-level的功能，如记录目录结构的tree object的实现
"""
import os
from collections import namedtuple, deque
import itertools
import operator
import string
from . import data


def is_ignore(full):
    return ".zxcgit" in full.split(os.sep)


'''
将dir目录抽象成tree对象写入.zxcgit/object
'''


def write_tree(dir_="."):
    entrys = []
    with os.scandir(dir_) as it:
        for entry in it:
            # 判断本身，而不是符号链接的指向
            full = os.path.join(dir_, entry.name)
            if is_ignore(full):
                continue
            if entry.is_file(follow_symlinks=False):
                with open(full, "rb") as f:
                    oid = data.hash_object(f.read())
                    entrys.append(("blob", oid, entry.name))
            elif entry.is_dir(follow_symlinks=False):
                oid = write_tree(full)
                entrys.append(("tree", oid, entry.name))

    tree = "\n".join([f"{type_} {oid} {name}" for type_, oid, name in entrys])
    return data.hash_object(tree.encode(), "tree")


#  对于当前tree对象，生成[(type_, oid, name), ... ]
def _iter_tree_entries(oid):
    tree = data.get_object(oid, "tree")
    for entry in tree.decode().splitlines():
        type_, oid, name = entry.split()
        yield type_, oid, name


'''
res = {blob_path:blob_oid
'''


def get_tree(oid, base_path="."):
    res = {}
    for type_, oid, name in _iter_tree_entries(oid):
        path = os.path.join(base_path, name)
        if type_ == "blob":
            res[path] = oid
        elif type_ == "tree":
            # 将新字典更新到res
            res.update(get_tree(oid, path))
        else:
            assert False, f"{type_} is not a tree entry"
    return res


def _empty_repo():
    for root, dirs, files in os.walk(".", topdown=False):
        for file in files:
            path = os.path.join(root, file)
            # print(path)
            if is_ignore(path):
                continue
            os.remove(path)
        for dir_ in dirs:
            path = os.path.join(root, dir_)
            if is_ignore(path):
                continue
            try:
                os.rmdir(path)
            except(FileNotFoundError, OSError):
                pass


# get_object(oid)----> path
def read_tree(oid):
    _empty_repo()
    # {}.item()获得[(key,value)...]
    for path, oid in get_tree(oid).items():
        # 递归创建目录，如果已存在不报错
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as out:
            out.write(data.get_object(oid, "blob"))


def commit(message):
    res = f"tree {write_tree()}\n"
    HEAD = data.get_ref("HEAD")
    # 如果是第一次commit，会返回none
    if HEAD:
        res += f'parent {HEAD}\n'
    res += '\n'
    res += message

    oid = data.hash_object(res.encode(), "commit")
    data.update_ref("HEAD", oid)
    return oid


Commit = namedtuple("Commit", ["tree", "parent", "message"])


def get_commit(oid):
    parent = None
    commit_ = data.get_object(oid, "commit").decode()
    lines = iter(commit_.splitlines())
    for line in itertools.takewhile(operator.truth, lines):
        type_, oid = line.split()
        if type_ == "tree":
            tree = oid
        elif type_ == "parent":
            parent = oid
        else:
            assert False, f"Unknown field {type_}"

    message = "\n".join(lines)
    return Commit(tree, parent, message)


def checkout(oid):
    commit_ = get_commit(oid)
    read_tree(commit_.tree)
    data.update_ref("HEAD", oid)


def create_tag(name, oid):
    ref_path = os.path.join("refs", "tags", f"{name}")
    data.update_ref(ref_path, oid)


def creat_branch(name, oid):
    branch_path = os.path.join("refs", "heads", f"{name}")
    data.update_ref(branch_path, oid)


def get_oid(name):
    if name == "@":
        name = "HEAD"
    # is a ref
    path_search = [
        os.path.join(f"{name}"),
        os.path.join("refs", f"{name}"),
        os.path.join("refs", "tags", f"{name}"),
        os.path.join("refs", "heads", f"{name}")
    ]
    for path in path_search:
        if data.get_ref(path):
            return data.get_ref(path)
    # is a oid
    is_hex = all(c in string.hexdigits for c in name)
    if len(name) == 40 and is_hex:
        return name
    assert False, f"Unknown name {name}"


def iter_commit_parents(oids):
    oids = deque(oids)
    visited = set()
    while oids:
        oid = oids.popleft()
        if not oid or oid in visited:
            continue
        yield oid

        commit_ = get_commit(oid)
        oids.appendleft(commit_.parent)
