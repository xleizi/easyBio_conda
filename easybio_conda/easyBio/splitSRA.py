import argparse
import os
from pathlib import Path

from .Utils import splitSRAfun
from .Utils import createDir, get_num_threads

def main():
    num_threads = get_num_threads()
   # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Process .sra files with parallel-fastq-dump")
    parser.add_argument("-f", "--folder", default=".",
                        help="Folder containing .sra files (default: current directory)")
    parser.add_argument("-t", "--threads", type=int, default=num_threads,
                        help="Number of threads (default: your cpucounts)")
    parser.add_argument("-o", "--outdir", default="./",
                        help="Output directory (default: out)")
    parser.add_argument("-k", "--kind", default="--split-files",
                        help="Zhe kind of split")

    args = parser.parse_args()
    
    current_path = os.getcwd()
    
    folder = args.folder
    outdir = args.outdir
    threads = args.threads
    kind = args.kind
    
    print("\033[1;32m GSE folder:\033[0m \033[32m{}\033[0m".format(folder))
    print("\033[1;32m outdir:\033[0m \033[32m{}\033[0m".format(outdir))
    print("\033[1;32m threads:\033[0m \033[32m{}\033[0m".format(threads))
    print("\033[1;32m kind:\033[0m \033[32m{}\033[0m".format(kind))

    # Create output directory if it doesn't exist
    createDir(outdir)
    splitSRAfun(folder, outdir, threads, kind)


if __name__ == "__main__":
    main()
