import sys

from .Utils.easyBioUtils import cellrangerRun


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <db_path> <fq_dir_path> <expect_cell_num>")
        sys.exit(1)

    db = sys.argv[1]
    fq_dir = sys.argv[2]
    expectcellnum = sys.argv[3]

    cellrangerRun(db, fq_dir, expectcellnum)
