import argparse
from . import data
from . import base
import os
import sys


def main():
    args = parse_arg()
    args.func(args)


def parse_arg():
    # 添加命令解释器
    parser = argparse.ArgumentParser()
    # 添加子命令解释器
    commands = parser.add_subparsers(dest='commands')
    # 必须要输入子命令才能执行
    commands.required = True
    # 添加init命令
    init_parser = commands.add_parser('init')
    init_parser.set_defaults(func=init)

    # 添加hash_object命令
    hash_object_parser = commands.add_parser('hash_object')
    hash_object_parser.set_defaults(func=hash_object)
    hash_object_parser.add_argument('file')

    # zxcgit cat_file oid
    cat_file_parser = commands.add_parser('cat_file')
    cat_file_parser.set_defaults(func=cat_file)
    cat_file_parser.add_argument('oid')

    write_tree_parser = commands.add_parser('write_tree')
    write_tree_parser.set_defaults(func=write_tree)

    return parser.parse_args()


def init(args):
    data.init()
    print('Successfully Initialized Empty Git Repository in %s' % os.path.join(os.getcwd(), data.GIT_DIR))
    # print(f"Successfully Initialized Empty Git Repository in {os.getcwd()}/{data.GIT_DIR}")


def hash_object(args):
    with open(args.file, 'rb') as f:
        print(data.hash_object(f.read()))


def cat_file(args):
    sys.stdout.flush()
    sys.stdout.buffer.write(data.get_object(args.oid))


def write_tree(args):
    print(base.write_tree())
