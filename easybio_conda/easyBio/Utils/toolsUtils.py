# -*- coding: utf-8 -*-
# Author: Lei
# Date: 2023-04-20
# Description:
import shutil
import datetime
import multiprocessing
import os
import hashlib
import sys

import psutil

def calMd5(filename):
    with open(filename,"rb") as f:
        bytes = f.read() # read file as bytes
        readable_hash = hashlib.md5(bytes).hexdigest();
        return readable_hash


def sraMd5Cal(folder, md5List, rawdirs):
    sraFiles = os.listdir(folder)
    reDownloadSra = []
    # file= open(f"{rawdirs}/md5check","r")
    # scItems = file.readlines()
    # print(scItems)
    # print(sraFiles)
    
    md5checkFile = f"{rawdirs}/md5check"
    if os.path.exists(md5checkFile):
        file = open(md5checkFile, "r")
        scItems = file.readlines()
    else:
        scItems = []
    scItems = [item.replace("\n","") for item in scItems]
    # print(scItems)
    
    with open(md5checkFile, "a+") as file:
        for md5Item in md5List.keys():
            if md5Item in sraFiles:
                if not md5Item in scItems:
                    print(f"计算{md5Item}文件的md5值")
                    calMd5filName = f"{folder}/{md5Item}"
                    cd5 = calMd5(calMd5filName)
                    # print(cd5)
                    # print(md5List[md5Item])
                    print(cd5 == md5List[md5Item])
                    if cd5 != md5List[md5Item]:
                        os.remove(calMd5filName)
                        reDownloadSra.append(md5Item)
                    else:
                        # f.write(md5Item)
                        file.writelines(md5Item)
                        file.writelines("\n")
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
    # num_threads = multiprocessing.cpu_count()
    num_threads = os.cpu_count()
    if num_threads <= 16:
        num_threads -= 2
    elif num_threads < 64:
        num_threads -= 4
    elif num_threads < 128:
        num_threads -= 8
    else:
        num_threads -= 10
    return num_threads


def get_available_memory(unit="GB"):
    # num_threads = multiprocessing.cpu_count()
    memory_info = psutil.virtual_memory()
    memory_available = memory_info.available
    total_memory_gb = int(memory_available / (1024 ** 3))
    total_memory_mb = int(memory_available / (1024 ** 2))
    total_memory_kb = int(memory_available / (1024 ** 1))
    total_memory = total_memory_gb if unit == "GB" else (
        total_memory_mb if unit == "MB" else total_memory_kb)
    print("总可用内存：", total_memory, unit)
    return total_memory


def copyDirs(source_dir, target_dir):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    for file_name in os.listdir(source_dir):
        source_file = os.path.join(source_dir, file_name)
        target_file = os.path.join(target_dir, file_name)

        if os.path.isfile(source_file):
            shutil.copy2(source_file, target_file)
            print(f"Copied {source_file} to {target_file}")


def get_current_system():
    platform = sys.platform
    if platform.startswith('win'):
        return 'Windows'
    elif platform.startswith('linux'):
        return 'Linux'
    elif platform.startswith('darwin'):
        return 'Mac'
    else:
        return 'Unknown'