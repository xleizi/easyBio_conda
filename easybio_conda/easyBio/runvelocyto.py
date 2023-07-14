# -*- coding: utf-8 -*-
# Author: Lei
# Date: 2023-04-26
# Description:
import argparse
from .Utils import runvelocityc


# Function to parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Run velocyto in parallel")
    parser.add_argument("-rmf", "--rmsk_file", type=str, required=True,
                        help="Path to the hg38_rmsk.gtf file")
    parser.add_argument("-gtf", "--gtf_file", type=str, required=True,
                        help="Path to the Homo_sapiens.GRCh38.109.gtf file")
    parser.add_argument("-i", "--matrices_file", type=str,
                        required=True, help="Path to the matrices directory")
    parser.add_argument("-m", "--max_memory", type=int, default=200,
                        help="Maximum memory in GB (default: 200)")
    return parser.parse_args()

def main():
    # Parse command line arguments
    args = parse_args()
    rmsk_file = args.rmsk_file
    gtf_file = args.gtf_file
    matrices_file = args.matrices_file
    max_memory = args.max_memory

    if rmsk_file and gtf_file:
        rv = runvelocityc(matrices_file, rmsk_file, gtf_file, max_memory)
        rv.buildLoomFile()

# Main script execution
if __name__ == "__main__":
    main()