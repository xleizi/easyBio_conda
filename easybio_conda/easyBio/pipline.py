import multiprocessing
from pathlib import Path
import re
import os
from .Utils.downloadUtils import downLoadSRA
import argparse

from .Utils import cellrangerRun, splitSRAfun
from .Utils import createDir


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
    print("\033[1;32mAll files are already in Cell Ranger format.\033[0m")


if __name__ == "__main__":
    num_threads = multiprocessing.cpu_count()
    if num_threads <= 16:
        num_threads -= 2
    elif num_threads < 64:
        num_threads -= 4
    elif num_threads < 128:
        num_threads -= 8
    else:
        num_threads -= 10

    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Process GSE number, directory and threads")
    parser.add_argument("-g", "--gsenumber", help="GSE number")
    parser.add_argument("-d", "--dirs", default=os.getcwd(),
                        help="Directory (default: current directory)")
    parser.add_argument("-t", "--threads", type=int, default=num_threads,
                        help="Number of threads (default: your cpucounts)")
    parser.add_argument("-k", "--kind", default="--split-files",
                        help="Zhe kind of split")
    parser.add_argument("-db", "--db_path", required=True,
                        help="Path to the gene reference file (required)")
    parser.add_argument("-ec", "--expectcellnum", type=int, default=3000,
                        help="Expected cell number for running cellranger (default: 3000)")

    args = parser.parse_args()

    # Extract values from parsed arguments
    gsenumber = args.gsenumber
    dirs = args.dirs
    threads = args.threads
    kind = args.kind
    db_path = args.db_path
    expectcellnum = args.expectcellnum

    rawdirs = f"{dirs}/{gsenumber}/raw"

    # 下载 SRA 数据
    downLoadSRA(gsenumber, dirs, threads)

    print("\033[1;33m{}\033[0m".format("*" * 80))   # 黄

    folder = f"{dirs}/sra"
    outdir = f"{dirs}/fq"

    createDir(outdir)
    splitSRAfun(folder, outdir, threads, kind)

    # splitSRA(rawdirs, kind, threads)
    print("\033[1;33m{}\033[0m".format("*" * 80))   # 黄
    rename_files(f"{rawdirs}/fq")
    print("\033[1;33m{}\033[0m".format("*" * 80))   # 黄
    matricespath = f"{rawdirs}/matrices"
    createDir(matricespath)
    cellrangerRun(db_path, f"{rawdirs}/fq", expectcellnum, matricespath)
