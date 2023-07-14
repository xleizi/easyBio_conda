# -*- coding: utf-8 -*-
# Author: Lei
# Date: 2023-04-20
# Description:
from concurrent.futures import ThreadPoolExecutor
import os
import shutil
import subprocess
import concurrent

from .toolsUtils import get_num_threads



def splitSRAfun(folder, outdir, threads, kind):
    # Get a list of .sra files in the folder
    sra_files = [f for f in os.listdir(folder) if f.endswith('.sra')]

    # Iterate over .sra files in the folder and run the provided command
    for sra_file in sra_files:
        sra_base, _ = os.path.splitext(sra_file)

        output_files = [f for f in os.listdir(outdir) if f.startswith(f"{sra_base}_") and f.endswith(".fastq.gz")]

        if output_files:
            print(f"Skipping {sra_file} as output files already exist.")
            continue

        print(f"Processing {sra_file}...")

        cmd = [
            "parallel-fastq-dump",
            "--sra-id", os.path.join(folder, sra_file),
            "--threads", str(threads),
            "--outdir", outdir,
            kind,
            "--gzip"
        ]

        subprocess.run(cmd, check=True)
        print("\033[1;32m Finished processing", sra_file, "\033[0m")
    print("\033[1;32m All files processed.\033[0m")


def cellrangerRun(db, fq_dir, expectcellnum, otherItem="", matricespath="", ):
    # 获取文件夹中的所有文件名
    filenames = os.listdir(fq_dir)

    current_dir = os.getcwd()
    # 获取目录中所有的子目录
    subdirectories = [d for d in os.listdir(
        current_dir) if os.path.isdir(os.path.join(current_dir, d))]

    # 遍历子目录，检查是否以“SRR”开头
    for subdirectory in subdirectories:
        if subdirectory.startswith("SRR"):
            print("\033[1;31m Found residual folder, removing it...\033[0m")
            # 如果以“SSR”开头，则删除这个子目录及其内容
            subdirectory_path = os.path.join(current_dir, subdirectory)
            # rm -rf删的更快(*^▽^*)
            os.system(f"rm -rf {subdirectory_path}")

    # time.sleep(10000)
                
    samples = set()
    for filename in filenames:
        if filename.startswith("SRR"):
            sample_id = filename.split("_")[0]
            ## 剔除掉已存在的处理好的文件夹
            if matricespath != "":
                sample_dir = os.path.join(matricespath, sample_id)
                if not os.path.isdir(sample_dir):
                    samples.add(sample_id)
            else:
                samples.add(sample_id)

    if samples == set():
        print("\033[1;32m All samples have been processed with Cell Ranger\033[0m")
    else:
        print(samples)
         
    
    for sample in samples:
        cmd = f"""cellranger count --id={sample} \
--transcriptome={db} \
--fastqs={fq_dir} \
--sample={sample} \
--expect-cells={expectcellnum} \
--nosecondary {otherItem}"""

#         cmd = f"""cellranger count --id={sample} \
# --transcriptome={db} \
# --fastqs={fq_dir} \
# --sample={sample} \
# --expect-cells={expectcellnum}"""
        print("\033[1;33m Running command for sample {}:\033[0m".format(sample))
        print("\033[1;31m{}\033[0m".format(cmd))
        subprocess.run(cmd, shell=True)

        # result = subprocess.run(
        #     cmd, shell=True, capture_output=True, text=True)
        # output = result.stdout  # 获取输出结果
        # # 对输出结果进行运算
        # output_lines = output.splitlines()
        # pre = " ".join(output_lines[-20:-18])  # 获取最后20行中的前2行，并将它们连接为一个字符串
        # print(f"{sample} {pre}")

        
        if matricespath != "":
            mv_cmd = ["mv", f"{sample}", f"{matricespath}"]
            subprocess.run(mv_cmd, check=True)

# 多线程跑cellranger使用，目前看效果不大（比单线程快不了太多）
def run_cellranger(sample, core, db, fq_dir, expectcellnum, matricespath):
    ## --localmem = 128 \
    cmd = f"""cellranger count --id={sample} \
--localcores={core} \
--transcriptome={db} \
--fastqs={fq_dir} \
--sample={sample} \
--expect-cells={expectcellnum}"""
    print("\033[1;33m Running command for sample {}:\033[0m".format(sample))
    print("\033[1;31m{}\033[0m".format(cmd))
    subprocess.run(cmd, shell=True)
    if matricespath != "":
        mv_cmd = ["mv", f"{sample}", f"{matricespath}"]
        subprocess.run(mv_cmd, check=True)
        
        
def cellrangerRun2(db, fq_dir, expectcellnum, matricespath=""):
    # 获取文件夹中的所有文件名
    filenames = os.listdir(fq_dir)

    current_dir = os.getcwd()
    # 获取目录中所有的子目录
    subdirectories = [d for d in os.listdir(
        current_dir) if os.path.isdir(os.path.join(current_dir, d))]

    # 遍历子目录，检查是否以“SRR”开头
    for subdirectory in subdirectories:
        if subdirectory.startswith("SRR"):
            print("\033[1;31m Found residual folder, removing it...\033[0m")
            # 如果以“SSR”开头，则删除这个子目录及其内容
            subdirectory_path = os.path.join(current_dir, subdirectory)
            # rm -rf删的更快(*^▽^*)
            os.system(f"rm -rf {subdirectory_path}")

    # time.sleep(10000)

    samples = set()
    for filename in filenames:
        if filename.startswith("SRR"):
            sample_id = filename.split("_")[0]
            # 剔除掉已存在的处理好的文件夹
            if matricespath != "":
                sample_dir = os.path.join(matricespath, sample_id)
                if not os.path.isdir(sample_dir):
                    samples.add(sample_id)
    print(samples)
    
    folder_count = len(samples)
    
    for i in range(1, min(folder_count + 1, 21)):
        if folder_count % i == 0:
            max_workers = i
    
    num_threads = max_workers
    core = 100 // num_threads
    # 调用函数
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = {executor.submit(run_cellranger, sample, core, db, fq_dir,
                                expectcellnum, matricespath): sample for sample in samples}
        for future in concurrent.futures.as_completed(futures):
            sample = futures[future]
            try:
                future.result()
                print(f"Sample {sample} completed successfully.")
            except Exception as e:
                print(f"Sample {sample} encountered an error: {e}")


def check_file_exists(folder_path, target_suffix):
    for file_name in os.listdir(folder_path):
        if file_name.endswith(target_suffix):
            return True
    return False


def tidySummary(matrices_base, output_base):
    summary_base = os.path.join(output_base, "summary")
    matrix_base = os.path.join(output_base, "matrix")
    matrixh5_base = os.path.join(output_base, "matrixh5")
    loomFile_base = os.path.join(output_base, "loomfile")

    # 如果目标文件夹不存在，创建它
    os.makedirs(summary_base, exist_ok=True)
    os.makedirs(matrix_base, exist_ok=True)
    os.makedirs(matrixh5_base, exist_ok=True)
    os.makedirs(loomFile_base, exist_ok=True)

    for folder in os.listdir(matrices_base):
        src_folder = os.path.join(matrices_base, folder)

        if os.path.isdir(src_folder):
            src_file = os.path.join(src_folder, 'outs', 'web_summary.html')
            src_matrix_folder = os.path.join(
                src_folder, 'outs', 'filtered_feature_bc_matrix')
            matrixh5flie = os.path.join(
                src_folder, 'outs', 'filtered_feature_bc_matrix.h5')
            loomflie = os.path.join(
                src_folder, 'velocyto', f'{folder}.loom')

            if os.path.exists(src_file):
                dst_file = os.path.join(summary_base, folder + '.html')
                if not os.path.exists(dst_file):
                    try:
                        shutil.copy2(src_file, dst_file)
                    except:
                        pass
                
            if os.path.exists(src_matrix_folder):
                dst_matrix_folder = os.path.join(matrix_base, folder)
                if not os.path.exists(dst_matrix_folder):
                    try:
                        shutil.copytree(src_matrix_folder, dst_matrix_folder)
                    except:
                        pass
                    
            if os.path.exists(matrixh5flie):
                dst_matrixh5_folder = os.path.join(matrixh5_base, folder + '.h5')
                if not os.path.exists(dst_matrixh5_folder):
                    try:
                        shutil.copy2(matrixh5flie, dst_matrixh5_folder)
                    except:
                        pass
                    
            if os.path.exists(loomflie):
                dst_loom_folder = os.path.join(loomFile_base, folder + '.loom')
                if not os.path.exists(dst_loom_folder):
                    try:
                        shutil.copy2(loomflie, dst_loom_folder)
                    except:
                        pass
    print("\033[1;32m All output results have been organized.\033[0m")
    

