# -*- coding: utf-8 -*-
# Author: Lei
# Date: 2023-04-20
# Description:
import datetime
import multiprocessing
import os
import hashlib

def calMd5(filename):
    with open(filename,"rb") as f:
        bytes = f.read() # read file as bytes
        readable_hash = hashlib.md5(bytes).hexdigest();
        return readable_hash


def sraMd5Cal(folder, md5List):
    sraFiles = os.listdir(folder)
    reDownloadSra = []
    # print(sraFiles)
    for md5Item in md5List.keys():
        print(f"计算{md5Item}文件的md5值")
        if md5Item in sraFiles:
            calMd5filName = f"{folder}/{md5Item}"
            cd5 = calMd5(calMd5filName)
            # print(cd5)
            # print(md5List[md5Item])
            # print(cd5==md5List[md5Item])
            if cd5!=md5List[md5Item]:
                os.remove(calMd5filName)
        else:
            reDownloadSra.append(md5Item)
            
    print(reDownloadSra)
    return reDownloadSra
    
def del_files(dir_path):
    if os.path.isfile(dir_path):
        try:
            os.remove(dir_path)  # 这个可以删除单个文件，不能删除文件夹
        except BaseException as e:
            print(e)
    elif os.path.isdir(dir_path):
        file_lis = os.listdir(dir_path)
        for file_name in file_lis:
            # if file_name != 'wibot.log':
            tf = os.path.join(dir_path, file_name)
            del_files(tf)
    print('del files ok')


def getNowTime():
    curr_time = datetime.datetime.now()
    time_str = datetime.datetime.strftime(curr_time, '%Y-%m-%d %H:%M:%S')
    return time_str


def createDir(str):
    try:
        os.makedirs(str)
    except:
        pass


def get_num_threads():
    num_threads = multiprocessing.cpu_count()
    if num_threads <= 16:
        num_threads -= 2
    elif num_threads < 64:
        num_threads -= 4
    elif num_threads < 128:
        num_threads -= 8
    else:
        num_threads -= 10
    return num_threads
