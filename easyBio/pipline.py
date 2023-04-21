import math
import multiprocessing
from pathlib import Path
import re
import subprocess
import os
from Utils.downloadUtils import downLoadSRA, getbioproject
import argparse


def splitSRA(dirs, kind, threads):
    folder = Path(f"{dirs}/sra")
    outdir = Path(f"{dirs}/fq")

    # Create output directory if it doesn't exist
    outdir.mkdir(parents=True, exist_ok=True)

    # Iterate over .sra files in the folder and run the provided command
    for sra_file in folder.glob("*.sra"):
        sra_base = sra_file.stem

        # Check if output files already exist
        output_files = list(outdir.glob(f"{sra_base}_*.fastq.gz"))

        if output_files:
            print(
                "\033[1;32mSkipping {} as output files already exist.\033[0m".format(sra_file))
            continue

        print("\033[1;33mProcessing {}...\033[0m".format(sra_file))

        cmd = [
            "parallel-fastq-dump",
            "--sra-id", str(sra_file),
            "--threads", str(threads),
            "--outdir", str(outdir),
            kind,
            "--gzip"
        ]

        subprocess.run(cmd, check=True)
        print("\033[1;32mFinished processing {}\033[0m".format(sra_file))

    print("\033[1;32mAll files processed.\033[0m")


def rename_files(folder_path):
    # 创建一个空字典，用于存储SRR号及其出现的次数
    srr_counts = {}

    # 遍历文件夹中的所有文件
    for file in os.listdir(folder_path):
        # 使用正则表达式匹配文件名
        match = re.match(r'(SRR\d+)_(\d)', file)
        if match:
            srr_id, num = match.groups()
            srr_counts[srr_id] = max(srr_counts.get(srr_id, 0), int(num))

    # 根据文件数重命名文件

    for file in os.listdir(folder_path):
        match = re.match(r'(SRR\d+)_(\d)', file)
        if match:
            srr_id, num = match.groups()
            if srr_counts[srr_id] == 2:
                new_name = f'{srr_id}_S1_L001_R{num}_001.fastq.gz'
            elif srr_counts[srr_id] == 3:
                if num == "1":
                    new_name = f'{srr_id}_S1_L001_I1_001.fastq.gz'
                else:
                    new_name = f'{srr_id}_S1_L001_R{int(num)-1}_001.fastq.gz'
            os.rename(os.path.join(folder_path, file),
                      os.path.join(folder_path, new_name))
    print("\033[1;32mAll files are already in Cell Ranger format.\033[0m")


def cellrangerRun(db, fq_dir, matricespath, expectcellnum):
    # 获取文件夹中的所有文件名
    filenames = os.listdir(fq_dir)
    # print(matricespath)

    # 获取目录中所有的子目录
    subdirectories = [d for d in os.listdir(
        fq_dir) if os.path.isdir(os.path.join(fq_dir, d))]

    # 遍历子目录，检查是否以“SRR”开头
    for subdirectory in subdirectories:
        if subdirectory.startswith("SRR"):
            print("\033[1;31mFound residual folder, removing it...\033[0m")
            # 如果以“SSR”开头，则删除这个子目录及其内容
            subdirectory_path = os.path.join(fq_dir, subdirectory)
            os.system(f"rm -rf {subdirectory_path}")

    # time.sleep(10000)

    samples = set()
    for filename in filenames:
        if filename.startswith("SRR"):
            sample_id = filename.split("_")[0]
            samples.add(sample_id)

    # 遍历样本并运行cellranger count命令
    for sample in samples:
        # file_path = os.path.join(matricespath, sample)
        cmd = f"""cellranger count --id={sample} \
--transcriptome={db} \
--fastqs={fq_dir} \
--sample={sample} \
--expect-cells={expectcellnum} \
--nosecondary"""
        print("\033[1;33mRunning command for sample {}:\033[0m".format(sample))
        print("\033[1;31m{}\033[0m".format(cmd))
        subprocess.run(cmd, shell=True)
        mv_cmd = ["mv", f"{sample}", f"{matricespath}"]
        subprocess.run(mv_cmd, check=True)


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

    rawdirs = f"{dirs}/{gsenumber}/raw"

    # 下载 SRA 数据
    downLoadSRA(gsenumber, dirs, threads)

    print("\033[1;33m{}\033[0m".format("*" * 80))   # 黄

    splitSRA(rawdirs, kind, threads)
    print("\033[1;33m{}\033[0m".format("*" * 80))   # 黄
    # print("\033[1;31m{}\033[0m".format("=" * 80))   # 红
    # print("\033[1;32m{}\033[0m".format("-" * 80))   # 绿
    rename_files(f"{rawdirs}/fq")
    print("\033[1;33m{}\033[0m".format("*" * 80))   # 黄
    matricespath = Path(f"{rawdirs}/matrices")
    matricespath.mkdir(parents=True, exist_ok=True)
    cellrangerRun(db_path, f"{rawdirs}/fq", matricespath, expectcellnum)


# 移动所有.sra文件到sra目录，之后删除sra目录中所有不是.sra文件的文件
# os.system('find ./sra -mindepth 1 ! -name "*.sra" -delete')

# 更改文件名字
# rename_files(str(outdir))
