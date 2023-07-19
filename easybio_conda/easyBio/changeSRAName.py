# -*- coding: utf-8 -*-
# Author: Lei
# Date: 2023-04-20
# Description:
import argparse
from collections import defaultdict
import os
import re

def renames1(folder_path):
    # 创建一个空字典，用于存储SRR号及其出现的次数
    srr_counts = {}

    # 遍历文件夹中的所有文件
    for file in os.listdir(folder_path):
        # 使用正则表达式匹配文件名
        match = re.match(r'(SRR\d+)_(\d)', file)
        if match:
            srr_id, num = match.groups()
            srr_counts[srr_id] = max(srr_counts.get(srr_id, 0), int(num))

    # 根据文件数重命名文件
    for file in os.listdir(folder_path):
        match = re.match(r'(SRR\d+)_(\d)', file)
        if match:
            srr_id, num = match.groups()
            if srr_counts[srr_id] == 1 or 2:
                new_name = f'{srr_id}_S1_L001_R{num}_001.fastq.gz'
            elif srr_counts[srr_id] == 3:
                if num == "1":
                    new_name = f'{srr_id}_S1_L001_I1_001.fastq.gz'
                else:
                    new_name = f'{srr_id}_S1_L001_R{int(num)-1}_001.fastq.gz'
            elif srr_counts[srr_id] == 3:
                if num == "1":
                    new_name = f'{srr_id}_S1_L001_I1_001.fastq.gz'
                if num == "2":
                    new_name = f'{srr_id}_S1_L001_I2_001.fastq.gz'
                else:
                    new_name = f'{srr_id}_S1_L001_R{int(num)-2}_001.fastq.gz'
            
            os.rename(os.path.join(folder_path, file),
                      os.path.join(folder_path, new_name))
            print(f'Renamed {file} to {new_name}')

def read_mapping_file(list_file):
    with open(list_file, 'r') as f:
        lines = f.readlines()
        mapping = {line.split()[0]: line.split()[1] for line in lines}
    return mapping

def count_srr_occurrences(folder_path):
    files = os.listdir(folder_path)
    srr_counts = defaultdict(int)
    for file in files:
        srr_match = re.match(r'(SRR\d+)_(\d)', file)
        if srr_match:
            srr = srr_match.group(1)
            srr_counts[srr] += 1
    return files, srr_counts

def rename_files(files, folder_path, mapping, srr_counts):
    name_add_mapping = {}
    name_add_srr_mapping = {}
    for file in files:
        srr_match = re.match(r'(SRR\d+)_(\d)', file)
        if srr_match:
            srr, number = srr_match.groups()
            name = mapping[srr]
            read_type = ''
            if srr_counts[srr] == 2:
                read_type = 'R1' if number == '1' else 'R2'
            elif srr_counts[srr] == 3:
                read_type = 'I1' if number == '1' else (
                    'R1' if number == '2' else 'R2')

            if srr in name_add_srr_mapping:
                lane_number = name_add_srr_mapping[srr]
            else:
                name_add_mapping[name] = name_add_mapping.get(name, 0) + 1
                name_add_srr_mapping[srr] = name_add_mapping[name]
                lane_number = name_add_srr_mapping[srr]

            new_name = f"SRR{name}_S1_L00{lane_number}_{read_type}_001.fastq.gz"
            os.rename(os.path.join(folder_path, file),
                      os.path.join(folder_path, new_name))
            print(f'Renamed {file} to {new_name}')

def rename_files2(files, folder_path, mapping, srr_counts):
    name_add_mapping = {}
    name_add_srr_mapping = {}
    for file in files:
        srr_match = re.match(r'(SRR\d+)_(\d)', file)
        if srr_match:
            srr, number = srr_match.groups()
            name = mapping[srr]
            read_type = ''
            if srr_counts[srr] == 1 or 2:
                read_type = 'R1' if number == '1' else 'R2'
            elif srr_counts[srr] == 3:
                read_type = 'I1' if number == '1' else (
                    'R1' if number == '2' else 'R2')
            elif srr_counts[srr] == 4:
                read_type = 'I1' if number == '1' else (
                    'I2' if number == '2' else ('R1' if number == '3' else 'R2'))
                # match number:
                #     case '1':
                #         read_type = "I1"
                #     case '2':
                #         read_type = "I2"
                #     case '3':
                #         read_type = "R1"
                #     case '4':
                #         read_type = "R2"

            if srr in name_add_srr_mapping:
                lane_number = name_add_srr_mapping[srr]
            else:
                name_add_mapping[name] = name_add_mapping.get(name, 0) + 1
                name_add_srr_mapping[srr] = name_add_mapping[name]
                lane_number = name_add_srr_mapping[srr]

            new_name = f"SRR{name}_S{lane_number}_L001_{read_type}_001.fastq.gz"
            os.rename(os.path.join(folder_path, file),
                     os.path.join(folder_path, new_name))
            print(f'Renamed {file} to {new_name}')

def renames2(list_file, folder_path):
    mapping = read_mapping_file(list_file)
    files, srr_counts = count_srr_occurrences(folder_path)
    rename_files(files, folder_path, mapping, srr_counts)


def renames3(list_file, folder_path):
    mapping = read_mapping_file(list_file)
    files, srr_counts = count_srr_occurrences(folder_path)
    rename_files2(files, folder_path, mapping, srr_counts)

def renames4(mapping, folder_path):
    files, srr_counts = count_srr_occurrences(folder_path)
    print(mapping)
    rename_files2(files, folder_path, mapping, srr_counts)

def main():
    parser = argparse.ArgumentParser(
        description="Process list_file and folder_path")
    parser.add_argument("-l", "--list_file", help="matching list")
    parser.add_argument("-f", "--folder_path", default=os.getcwd(),
                        help="Directory (default: current directory)")

    args = parser.parse_args()

    list_file = args.list_file
    folder_path = args.folder_path
    
    print("\033[1;32m list_file:\033[0m \033[32m{}\033[0m".format(list_file))
    print("\033[1;32m folder_path:\033[0m \033[32m{}\033[0m".format(folder_path))
    
    if list_file:
        # renames2(list_file, folder_path)
        renames3(list_file, folder_path)
    else:
        renames1(folder_path)
    print("\033[1;32m Rename completed\033[0m")

if __name__ == '__main__':
    main()