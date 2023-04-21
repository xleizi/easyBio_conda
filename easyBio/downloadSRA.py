import math
import multiprocessing
import os
import argparse

from easyBio.tools.downloadTools import downLoadSRA

def main(gsenumber, dirs, threads, kind):
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

    args = parser.parse_args()
    
    gsenumber = args.gsenumber
    dirs = args.dirs
    threads = args.threads
    
    print("\033[1;32mGSE number:\033[0m \033[32m{}\033[0m".format(gsenumber))
    print("\033[1;32mDirectory:\033[0m \033[32m{}\033[0m".format(dirs))
    print("\033[1;32mThreads:\033[0m \033[32m{}\033[0m".format(threads))

    rawdirs = f"{dirs}/{gsenumber}/raw"

    # 计算下载线程数量
    max_download_thread = 50
    download_thread = min(max_download_thread, math.ceil(threads / 2))

    # 下载 SRA 数据
    downLoadSRA(gsenumber, dirs, download_thread)


if __name__ == "__main__":


    main()
