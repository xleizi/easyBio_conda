# -*- coding: utf-8 -*-
# Author: Lei
# Date: 2023-04-20
# Description:
import argparse
import os

from .Utils import downLoadSRA, getProResults
from .Utils import get_num_threads, sraMd5Cal

def main():
    num_threads = get_num_threads()

    parser = argparse.ArgumentParser(
        description="Process GSE number, directory and threads")
    parser.add_argument("-g", "--gsenumber", help="GSE number")
    parser.add_argument("-d", "--dirs", default=os.getcwd(),
                        help="Directory (default: current directory)")
    parser.add_argument("-t", "--threads", type=int, default=num_threads,
                        help="Number of threads (default: your cpucounts)")

    args = parser.parse_args()

        
    gsenumber = args.gsenumber
    dirs = args.dirs
    threads = args.threads

    print("\033[1;32mGSE number:\033[0m \033[32m{}\033[0m".format(gsenumber))
    print("\033[1;32mDirectory:\033[0m \033[32m{}\033[0m".format(dirs))
    print("\033[1;32mThreads:\033[0m \033[32m{}\033[0m".format(threads))

    # 下载 SRA 数据
    results = getProResults(gsenumber)
    md5List = {}
    for result in results:
        run_accession = f'${result["run_accession"]}.sra'
        sra_md5 = result["sra_md5"]
        md5List[run_accession] = sra_md5
    print(md5List)
        
    check = False
    while not check:
        # print(results)
        check = downLoadSRA(gsenumber, results, dirs, threads)
        
    # 下载 SRA 数据
    results = getProResults(gsenumber)
    
    md5List = {}
    for result in results:
        run_accession = f'{result["run_accession"]}.sra'
        sra_md5 = result["sra_md5"]
        md5List[run_accession] = sra_md5

    rawdirs = f"{dirs}/{gsenumber}/raw"
    filedirs = f"{dirs}/{gsenumber}/raw/sra"
    # reDownloadSra = sraMd5Cal(filedirs, md5List)
    
    reDownloadSra = [1, 2, 3]
    while len(reDownloadSra) > 1:
        check=False
        while not check:
            # print(results)
            check = downLoadSRA(gsenumber, results, dirs, threads)
        reDownloadSra = sraMd5Cal(filedirs, md5List, rawdirs)

if __name__ == "__main__":
    main()
