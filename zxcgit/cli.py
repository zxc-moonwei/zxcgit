import argparse
from . import data
from . import base
import os
import sys
import textwrap


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
    # zxcgit write_tree
    write_tree_parser = commands.add_parser('write_tree')
    write_tree_parser.set_defaults(func=write_tree)

    # zxcgit read_tree tree_oid
    read_tree_parser = commands.add_parser('read_tree')
    read_tree_parser.set_defaults(func=read_tree)
    read_tree_parser.add_argument('tree_oid')

    # zxcgit commit -m "message"
    commit_parser = commands.add_parser('commit')
    commit_parser.set_defaults(func=commit)
    commit_parser.add_argument('-m', '--message', required=True)

    # zxcgit log
    log_parser = commands.add_parser('log')
    log_parser.set_defaults(func=log)
    log_parser.add_argument('oid', nargs='?')

    # zxcgit checkout commit_oid
    checkout_parser = commands.add_parser('checkout')
    checkout_parser.set_defaults(func=checkout)
    checkout_parser.add_argument('oid')

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


def read_tree(args):
    base.read_tree(args.tree_oid)


def commit(args):
    print(base.commit(args.message))


def log(args):
    oid = args.oid or data.get_HEAD()
    while oid is not None:
        commit_ = base.get_commit(oid)
        print(f"commit {oid}")
        print(textwrap.indent(commit_.message, "    "))
        oid = commit_.parent


def checkout(args):
    base.checkout(args.oid)