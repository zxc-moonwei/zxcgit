"""
该模块将使用data模块提供的low-level功能，如对象存储，对象读取打印
来完成high-level的功能，如记录目录结构的tree object的实现
"""
import os

from . import data


def is_ignore(full):
    return ".zxcgit" in full.split(os.sep)


def write_tree(dir_="."):
    with os.scandir(dir_) as it:
        for entry in it:
            # 判断本身，而不是符号链接的指向
            full = os.path.join(dir_, entry.name)
            if is_ignore(full):
                continue
            if entry.is_file(follow_symlinks=False):
                with open(full, "rb") as f:
                    print(data.hash_object(f.read()), full)
            elif entry.is_dir(follow_symlinks=False):
                write_tree(full)

    # Todo 创建tree object
