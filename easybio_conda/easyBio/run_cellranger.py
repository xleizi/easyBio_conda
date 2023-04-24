import argparse

from .Utils import cellrangerRun


def main():
    parser = argparse.ArgumentParser(
            description="A script that processes input arguments.")
    
    parser.add_argument("-db", "--db_path", required=True,
                        help="Path to the gene reference file (required)")
    parser.add_argument("-fq", "--fq_dir_path", required=True,
                        help="Path to the fastq directory.")
    parser.add_argument("-ec", "--expectcellnum", type=int, default=3000,
                        help="Expected cell number for running cellranger (default: 3000)")
    
    args = parser.parse_args()

    db = args.db_path
    fq_dir = args.fq_dir_path
    expectcellnum = args.expectcellnum
    
    cellrangerRun(db, fq_dir, expectcellnum)

if __name__ == "__main__":
    main()
