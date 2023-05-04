import argparse
from . import data
import os


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

    return parser.parse_args()


def init(args):
    data.init()
    print('Successfully Initialized Empty Git Repository in %s' % os.path.join(os.getcwd(), data.GIT_DIR))
    # print(f"Successfully Initialized Empty Git Repository in {os.getcwd()}/{data.GIT_DIR}")


def hash_object(args):
    with open(args.file, 'rb') as f:
        print(data.hash_object(f.read()))
