import multiprocessing
import os

from changeSRAName import renames1
from changeSRAName import renames2
from .Utils import downLoadSRA
import argparse

from .Utils import cellrangerRun, splitSRAfun
from .Utils import createDir



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

    # 下载 SRA 数据
    downLoadSRA(gsenumber, dirs, threads)

    print("\033[1;33m{}\033[0m".format("*" * 80))   # 黄

    folder = f"{dirs}/sra"
    outdir = f"{dirs}/fq"

    createDir(outdir)
    splitSRAfun(folder, outdir, threads, kind)

    # splitSRA(rawdirs, kind, threads)
    print("\033[1;33m{}\033[0m".format("*" * 80))   # 黄
    
    # rename_files(f"{rawdirs}/fq")
    fqfiles = f"{rawdirs}/fq"
    if list_file:
        renames2(list_file, fqfiles)
    else:
        renames1(fqfiles)
    print("\033[1;32m Rename completed\033[0m")
    
    print("\033[1;33m{}\033[0m".format("*" * 80))   # 黄
    matricespath = f"{rawdirs}/matrices"
    createDir(matricespath)
    cellrangerRun(db_path, fqfiles, expectcellnum, matricespath)
