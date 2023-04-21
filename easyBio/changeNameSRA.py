import os
import re


def rename_files(folder_path):
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
            if srr_counts[srr_id] == 2:
                new_name = f'{srr_id}_S1_L001_R{num}_001.fastq.gz'
            elif srr_counts[srr_id] == 3:
                if num == "1":
                    new_name = f'{srr_id}_S1_L001_I1_001.fastq.gz'
                else:
                    new_name = f'{srr_id}_S1_L001_R{int(num)-1}_001.fastq.gz'
            os.rename(os.path.join(folder_path, file),
                      os.path.join(folder_path, new_name))


# 将此处的路径更改为你的文件夹路径
folder_path = "/home/data/user/lei/SRAData/GSE/GSE171539/raw/fq2"
rename_files(folder_path)
