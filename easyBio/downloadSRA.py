import os
import argparse

from Utils.downloadUtils import downLoadSRA
from easyBio.Utils.toolsUtils import get_num_threads


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

    args = parser.parse_args()

    gsenumber = args.gsenumber
    dirs = args.dirs
    threads = args.threads

    print("\033[1;32mGSE number:\033[0m \033[32m{}\033[0m".format(gsenumber))
    print("\033[1;32mDirectory:\033[0m \033[32m{}\033[0m".format(dirs))
    print("\033[1;32mThreads:\033[0m \033[32m{}\033[0m".format(threads))

    # rawdirs = f"{dirs}/{gsenumber}/raw"

    # 下载 SRA 数据
    downLoadSRA(gsenumber, dirs, threads)


if __name__ == "__main__":
    main()
