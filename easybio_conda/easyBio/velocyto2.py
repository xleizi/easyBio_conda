import os
import sys
import argparse
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed


def parse_args():
    parser = argparse.ArgumentParser(description="Run velocyto in parallel")
    parser.add_argument("--rmsk_file", type=str, required=True,
                        help="Path to the hg38_rmsk.gtf file")
    parser.add_argument("--gtf_file", type=str, required=True,
                        help="Path to the Homo_sapiens.GRCh38.109.gtf file")
    parser.add_argument("--matrices_file", type=str,
                        required=True, help="Path to the matrices directory")
    parser.add_argument("--max_memory", type=int, default=200,
                        help="Maximum memory in GB (default: 200)")
    return parser.parse_args()


def run_velocyto(directory, rmsk_file, gtf_file, num_threads):
    cmd = f'velocyto run10x -m {rmsk_file} {matrices_file}/{directory} {gtf_file} -@ {num_threads}'
    subprocess.run(cmd, shell=True)


def check_existing_loom(directory):
    velocyto_dir = os.path.join(directory, 'velocyto')
    if os.path.exists(velocyto_dir) and os.path.isdir(velocyto_dir):
        loom_files = [f for f in os.listdir(
            velocyto_dir) if f.endswith('.loom')]
        if len(loom_files) == 1:
            return True
    return False


if __name__ == "__main__":
    # args = parse_args()

    rmsk_file = "/home/data/user/lei/pipeline/rna/hg38_rmsk.gtf"
    gtf_file = "/home/data/user/lei/pipeline/rna/Homo_sapiens.GRCh38.109.gtf"
    matrices_file = "/home/data/user/lei/SRAData/GSE/GSE171539/raw/matrices"
    max_memory = 200
    # rmsk_file = args.rmsk_file
    # gtf_file = args.gtf_file
    # matrices_file = args.matrices_file
    # max_memory = args.max_memory

    print(len(os.listdir(matrices_file)))
    
    num_threads = min(20, (max_memory // 2) // len(os.listdir(matrices_file)))

    folders = [f for f in os.listdir(matrices_file) if os.path.isdir(
        os.path.join(matrices_file, f))]

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = {executor.submit(run_velocyto, folder, rmsk_file, gtf_file, num_threads)
                                   : folder for folder in folders if not check_existing_loom(os.path.join(matrices_file, folder))}

        for future in as_completed(futures):
            folder = futures[future]
            try:
                future.result()
                print(f"Folder {folder} completed successfully.")
            except Exception as e:
                print(f"Folder {folder} encountered an error: {e}")


# ThreadPoolExecutor的最大线程改为matrices_file下文件夹的个数，如果个数大于20则取20以下matrices_file下文件夹的个数最大可除尽的数
# num_threads改为max_memory除以2舍去余数，再除以ThreadPoolExecutor的最大线程数
