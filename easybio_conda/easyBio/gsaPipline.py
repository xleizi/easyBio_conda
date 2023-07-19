import os
import pandas as pd

from .runvelocyto import buildLoomFile

from .Utils import runvelocityc
from .Utils import tidySummary, getProResults, sraMd5Cal
from .Utils import get_num_threads, calMd5, gsaProject

from .changeSRAName import renames1, renames2, renames3
from .Utils import check_file_exists, cellrangerRun, splitSRAfun, downLoadSRA, cellrangerRun2
import argparse

def main():
    num_threads = get_num_threads()
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Process GSA number, directory and threads")
    parser.add_argument("-i", "--inputName", help="Project Number")
    parser.add_argument("-d", "--dirs", default=os.getcwd(),
                        help="Directory (default: current directory)")
    parser.add_argument("-t", "--threads", type=int, default=num_threads,
                        help="Number of threads (default: your cpucounts)")
    
    parser.add_argument("-db", "--db_path", required=True,
                        help="Path to the gene reference file (required)")
    parser.add_argument("-ec", "--expectcellnum", type=int, default=3000,
                        help="Expected cell number for running cellranger (default: 3000)")
    parser.add_argument("-oi", "--other_Item", type=str,
                        default="", help="otherItem for cellranger")
    parser.add_argument("-rmf", "--rmsk_file", type=str,
                        help="Path to the hg38_rmsk.gtf file")
    parser.add_argument("-gtf", "--gtf_file", type=str,
                        help="Path to the Homo_sapiens.GRCh38.109.gtf file")
    parser.add_argument("-vm", "--max_memory", type=int,
                        default=200, help="Maximum memory in GB (default: 200)")


    args = parser.parse_args()
    inputName = args.inputName
    dirs = args.dirs
    threads = args.threads
    db_path = args.db_path
    expectcellnum = args.expectcellnum
    rmsk_file = args.rmsk_file
    gtf_file = args.gtf_file
    max_memory = args.max_memory
    otherItem = args.other_Item

    gsap = gsaProject(inputName=inputName, dirs_path=dirs)
    gsap.downloadFiles(threads=threads, copy=True)
    gsap.renamegsa()
    
    print("\033[1;33m{}\033[0m".format("*" * 80))   # 黄
    gsap.cellrangerRun(db_path, expectcellnum, otherItem)
    print("\033[1;33m{}\033[0m".format("*" * 80))   # 黄

    if rmsk_file and gtf_file:
        rv = runvelocityc(gsap.matrices_path, rmsk_file, gtf_file, max_memory)
        rv.buildLoomFile()
    
    outputpath = f"{gsap.raw_path}/output"
    os.makedirs(outputpath, exist_ok=True)
    tidySummary(gsap.matrices_path, outputpath)

        
