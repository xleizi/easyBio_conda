# -*- coding: utf-8 -*-
# Author: Lei
# Date: 2023-04-20
# Description:
import os

from .Utils import tidySummary, getProResults, sraMd5Cal
from .Utils import get_num_threads, calMd5

from .changeSRAName import renames1, renames2, renames3
from .Utils import check_file_exists, cellrangerRun, splitSRAfun, downLoadSRA, cellrangerRun2
import argparse


# def writeLog(logname, logcontent):
#     with open(f"{logFiles}/{logname}", 'w') as file:
#         file.write(logcontent)


def main():
    num_threads = get_num_threads()

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
    parser.add_argument("-l", "--list_file", help="matching list")
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
    list_file = args.list_file

    rawdirs = f"{dirs}/{gsenumber}/raw"
    # logdirs = f"{rawdirs}/log"

    # splitSRA(rawdirs, kind, threads)
    folder = f"{rawdirs}/sra"
    fqfiles = f"{rawdirs}/fq"
    os.makedirs(folder, exist_ok=True)
    os.makedirs(fqfiles, exist_ok=True)

    print("\033[1;33m{}\033[0m".format(folder))   # 黄
    print("\033[1;33m{}\033[0m".format(fqfiles))   # 黄
    
    # os.makedirs(logdirs, exist_ok=True)

    # 下载 SRA 数据
    results = getProResults(gsenumber)
    
    md5List = {}
    for result in results:
        run_accession = f'{result["run_accession"]}.sra'
        sra_md5 = result["sra_md5"]
        md5List[run_accession] = sra_md5
    # print(md5List)
    
    # reDownloadSra = sraMd5Cal(folder, md5List)
    
    reDownloadSra = [1, 2, 3]
    while len(reDownloadSra) > 1:
        check=False
        while not check:
            # print(results)
            check = downLoadSRA(gsenumber, results, dirs, threads)
        reDownloadSra = sraMd5Cal(folder, results)
        
    
    print("\033[1;33m{}\033[0m".format("*" * 80))   # 黄


    target_suffix = 'S1_L001_R1_001.fastq.gz'
    file_exists = check_file_exists(fqfiles, target_suffix)

    if file_exists:
        print(f"fastq文件已进行改名")
    else:
        splitSRAfun(folder, fqfiles, threads, kind)
        
        print("\033[1;33m{}\033[0m".format("*" * 80))   # 黄
        if list_file:
            renames3(list_file, fqfiles)
        else:
            renames1(fqfiles)
        print("\033[1;32m Rename completed\033[0m")

    print("\033[1;33m{}\033[0m".format("*" * 80))   # 黄
    matricespath = f"{rawdirs}/matrices"
    os.makedirs(matricespath, exist_ok=True)
    cellrangerRun(db_path, fqfiles, expectcellnum, matricespath)
    
    outputpath = f"{rawdirs}/output"
    os.makedirs(outputpath, exist_ok=True)

    print("\033[1;33m{}\033[0m".format("*" * 80))   # 黄
    # 设置源文件夹和目标文件夹的路径
    tidySummary(matricespath, outputpath)


if __name__ == "__main__":
    main()