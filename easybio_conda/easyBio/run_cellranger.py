# -*- coding: utf-8 -*-
# Author: Lei
# Date: 2023-04-20
# Description:
import argparse

from .Utils import cellrangerRun, cellrangerRun2, easyCellranger


def main():
    parser = argparse.ArgumentParser(
            description="A script that processes input arguments.")
    
    parser.add_argument("-db", "--db_path", required=True,
                        help="Path to the gene reference file (required)")
    parser.add_argument("-fq", "--fq_dir_path", required=True,
                        help="Path to the fastq directory.")
    parser.add_argument("-ec", "--expectcellnum", type=int, default=3000,
                        help="Expected cell number for running cellranger (default: 3000)")
    parser.add_argument("-oi", "--other_Item", type=str,
                        default="", help="otherItem for cellranger")
    parser.add_argument("-mp", "--matricespath", type=str,
                        default="", help="Path to the  matrices directory")
    
    args = parser.parse_args()

    db = args.db_path
    fq_dir = args.fq_dir_path
    expectcellnum = args.expectcellnum
    otherItem = args.other_Item
    matricespath = args.matricespath

    ec = easyCellranger(fq_dir, expectcellnum,
                        db, otherItem, matricespath)
    ec.cellrangerRun()

if __name__ == "__main__":
    main()
