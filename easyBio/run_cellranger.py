import os
import subprocess
import sys


def main(db, fq_dir, expectcellnum):
    # 获取文件夹中的所有文件名
    filenames = os.listdir(fq_dir)

    # 提取SRRxxxxxx样本
    samples = set()
    for filename in filenames:
        if filename.startswith("SRR"):
            sample_id = filename.split("_")[0]
            samples.add(sample_id)

    # 遍历样本并运行cellranger count命令
    for sample in samples:
        file_path = os.path.join(fq_dir, sample)
        cmd = f"""cellranger count --id={sample} \
--transcriptome={db} \
--fastqs={fq_dir} \
--sample={sample} \
--expect-cells={expectcellnum} \
--nosecondary"""
        print(f"Running command for sample {sample}:")
        print(cmd)
        subprocess.run(cmd, shell=True)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <db_path> <fq_dir_path> <expect_cell_num>")
        sys.exit(1)

    db = sys.argv[1]
    fq_dir = sys.argv[2]
    expectcellnum = sys.argv[3]

    main(db, fq_dir, expectcellnum)
