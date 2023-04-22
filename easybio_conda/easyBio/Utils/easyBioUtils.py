import os
import subprocess


import os
import subprocess

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



def splitSRAfun2(folder, outdir, threads, kind):
    # Iterate over .sra files in the folder and run the provided command
    for sra_file in folder.glob("*.sra"):
        sra_base = sra_file.stem

        output_files = list(outdir.glob(f"{sra_base}_*.fastq.gz"))

        if output_files:
            print(f"Skipping {sra_file} as output files already exist.")
            continue

        print(f"Processing {sra_file}...")

        cmd = [
            "parallel-fastq-dump",
            "--sra-id", str(sra_file),
            "--threads", str(threads),
            "--outdir", str(outdir),
            kind,
            "--gzip"
        ]

        subprocess.run(cmd, check=True)
        print("\033[1;32m Finished processing", sra_file, "\033[0m")
    print("\033[1;32m All files processed.\033[0m")

def cellrangerRun(db, fq_dir, expectcellnum, matricespath=""):
    # 获取文件夹中的所有文件名
    filenames = os.listdir(fq_dir)

    # 获取目录中所有的子目录
    subdirectories = [d for d in os.listdir(
        fq_dir) if os.path.isdir(os.path.join(fq_dir, d))]

    # 遍历子目录，检查是否以“SRR”开头
    for subdirectory in subdirectories:
        if subdirectory.startswith("SRR"):
            print("\033[1;31m Found residual folder, removing it...\033[0m")
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
        cmd = f"""cellranger count --id={sample} \
--transcriptome={db} \
--fastqs={fq_dir} \
--sample={sample} \
--expect-cells={expectcellnum} \
--nosecondary"""
        print("\033[1;33m Running command for sample {}:\033[0m".format(sample))
        print("\033[1;31m{}\033[0m".format(cmd))
        subprocess.run(cmd, shell=True)
        if matricespath != "":
            mv_cmd = ["mv", f"{sample}", f"{matricespath}"]
            subprocess.run(mv_cmd, check=True)
