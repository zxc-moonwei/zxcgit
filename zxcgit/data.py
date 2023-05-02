# 管理.zxcgit 目录里面的数据

import os

GIT_DIR = '.zxcgit'

def init():
    os.makedirs(GIT_DIR)