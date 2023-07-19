# -*- coding: utf-8 -*-
# Author: Lei
# Date: 2023-04-20
# Description:
import math
import os

from .Utils import runvelocityc, toFastq, easyCellranger

from .Utils import tidySummary, getProResults, sraMd5Cal
from .Utils import get_num_threads, Download, downLoadBAM

from .changeSRAName import renames1, renames2, renames3, renames4, read_mapping_file
from .Utils import check_file_exists, cellrangerRun, splitSRAfun, downLoadSRA, cellrangerRun2
import argparse



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
    parser.add_argument("-df", "--DownloadFirst", type=bool, default=False,
                        help="Download sra data first")
    parser.add_argument("-k", "--kind", default="--split-files",
                        help="Zhe kind of split")
    parser.add_argument("-l", "--list_file", help="matching list")
    parser.add_argument("-db", "--db_path", required=True,
                        help="Path to the gene reference file (required)")
    parser.add_argument("-ec", "--expectcellnum", type=int, default=3000,
                        help="Expected cell number for running cellranger (default: 3000)")
    parser.add_argument("-rmf", "--rmsk_file", type=str, help="Path to the hg38_rmsk.gtf file")
    parser.add_argument("-gtf", "--gtf_file", type=str, help="Path to the Homo_sapiens.GRCh38.109.gtf file")
    parser.add_argument("-vm", "--max_memory", type=int,
                        default=200, help="Maximum memory in GB (default: 200)")
    parser.add_argument("-oi", "--other_Item", type=str,
                        default="", help="otherItem for cellranger")
    
    args = parser.parse_args()
    
    # Extract values from parsed arguments
    gsenumberList = args.gsenumber
    dirs = args.dirs
    threads = args.threads
    kind = args.kind
    db_path = args.db_path
    expectcellnum = args.expectcellnum
    list_file = args.list_file
    rmsk_file = args.rmsk_file
    gtf_file = args.gtf_file
    max_memory = args.max_memory
    otherItem = args.other_Item
    downloadFist = args.DownloadFirst
    
    gList = gsenumberList.split(",")
    print(gList)
    
    if downloadFist:
        for gsenumber in gList:
            rawdirs = f"{dirs}/{gsenumber}/raw"
            # folder = f"{rawdirs}/sra"
            # os.makedirs(folder, exist_ok=True)

            # print("\033[1;33m{}\033[0m".format(folder))   # 黄

            # 下载 SRA 数据
            results = getProResults(gsenumber)

            ds = downLoadSRA(results, rawdirs, threads)
            print(ds.md5List)
            print(ds.sampleMap)
            
            if ds.md5List == {}:
                db = downLoadBAM(results, rawdirs, threads)
                db.Download()
            else:
               ds.Download()
            print("\033[1;33m{}\033[0m".format("*" * 80))   # 黄

    for gsenumber in gList:
        rawdirs = f"{dirs}/{gsenumber}/raw"
        # folder = f"{rawdirs}/sra"
        # os.makedirs(folder, exist_ok=True)

        # print("\033[1;33m{}\033[0m".format(folder))   # 黄

        # 下载 SRA 数据
        results = getProResults(gsenumber)

        ds = downLoadSRA(results, rawdirs, threads)
        print(ds.md5List)

        if ds.md5List == {}:
            db = downLoadBAM(results, rawdirs, threads)
            db.Download()
            tofq = toFastq(db.bamfolder, type="bam", FastqDir=f"{rawdirs}/fq", threads=threads)
            tofq.BAMtoFastq(f"{rawdirs}/tofq")
            # exit()
        else:
            ds.Download()
            tofq = toFastq(ds.srafolder, FastqDir=f"{rawdirs}/fq", threads=threads)
            tofq.SRAtoFastq(kind)
            if list_file:
                sampleMap = read_mapping_file(list_file)
            else:
                sampleMap = ds.sampleMap
            tofq.renameFQfiles(sampleMap, folder_path=tofq.FastqDir)
        
        print("\033[1;33m{}\033[0m".format("*" * 80))   # 黄
        ec = easyCellranger(f"{rawdirs}/fq", expectcellnum,
                            db_path, otherItem, f"{rawdirs}/matrices")
        ec.cellrangerRun()
        
        print("\033[1;33m{}\033[0m".format("*" * 80))   # 黄
        
        if rmsk_file and gtf_file:
            rv = runvelocityc(ec.matricespath,
                              rmsk_file, gtf_file, max_memory)
            rv.buildLoomFile()

        outputpath = f"{rawdirs}/output"
        os.makedirs(outputpath, exist_ok=True)
        # 设置源文件夹和目标文件夹的路径
        tidySummary(ec.matricespath, outputpath)

if __name__ == "__main__":
    main()