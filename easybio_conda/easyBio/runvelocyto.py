# -*- coding: utf-8 -*-
# Author: Lei
# Date: 2023-04-26
# Description:
import os
import sys
import argparse
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

# Function to parse command line arguments


def parse_args():
    parser = argparse.ArgumentParser(description="Run velocyto in parallel")
    parser.add_argument("-rmf", "--rmsk_file", type=str, required=True,
                        help="Path to the hg38_rmsk.gtf file")
    parser.add_argument("-g", "--gtf_file", type=str, required=True,
                        help="Path to the Homo_sapiens.GRCh38.109.gtf file")
    parser.add_argument("-i", "--matrices_file", type=str,
                        required=True, help="Path to the matrices directory")
    parser.add_argument("-m", "--max_memory", type=int, default=200,
                        help="Maximum memory in GB (default: 200)")
    return parser.parse_args()

# Function to run velocyto command for a given directory


def run_velocyto(directory, rmsk_file, gtf_file, matrices_file, num_threads):
    cmd = f'velocyto run10x -m {rmsk_file} {matrices_file}/{directory} {gtf_file} -@ {num_threads}'
    subprocess.run(cmd, shell=True)

# Function to check if a directory contains any loom files


def check_existing_loom(directory):
    velocyto_dir = os.path.join(directory, 'velocyto')
    if os.path.exists(velocyto_dir) and os.path.isdir(velocyto_dir):
        loom_files = [f for f in os.listdir(
            velocyto_dir) if f.endswith('.loom')]
        if len(loom_files) >= 1:
            return True
    return False

# Function to compute the maximum number of workers for ThreadPoolExecutor


def compute_max_workers(matrices_file):
    folders = [f for f in os.listdir(matrices_file) if os.path.isdir(
        os.path.join(matrices_file, f)) and not check_existing_loom(os.path.join(matrices_file, f))]
    folder_count = len(folders)
    max_workers = 1
    for i in range(1, min(folder_count+1, 21)):
        if folder_count % i == 0:
            max_workers = i
    return max_workers


def main():
    # Parse command line arguments
    args = parse_args()
    rmsk_file = args.rmsk_file
    gtf_file = args.gtf_file
    matrices_file = args.matrices_file
    max_memory = args.max_memory

    # Compute the number of workers and threads for parallel execution
    max_workers = compute_max_workers(matrices_file)
    num_threads = (max_memory // 2) // max_workers

    # Get the list of folders to process, excluding those with existing loom files
    folders = [f for f in os.listdir(matrices_file) if os.path.isdir(
        os.path.join(matrices_file, f)) and not check_existing_loom(os.path.join(matrices_file, f))]
    print(folders)
    # Run velocyto in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(
            run_velocyto, folder, rmsk_file, gtf_file, matrices_file, num_threads): folder for folder in folders}
        # Process the results and print the status for each folder
        for future in as_completed(futures):
            folder = futures[future]
# Main script execution
if __name__ == "__main__":
    main()

