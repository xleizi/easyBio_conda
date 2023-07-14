import os
import subprocess
import time

class easyCellranger:
    def __init__(self, fq_dir, expectcellnum, db, otherItem="", matricespath="", threads=16) -> None:
        self.fq_dir = fq_dir
        self.expectcellnum = expectcellnum
        self.otherItem = otherItem
        self.db = db
        self.matricespath = matricespath
        self.threads = threads
        self.makOutPutdirs()
        self.getSampleList()
    
    def makOutPutdirs(self):
        os.makedirs(self.matricespath, exist_ok=True)

    def getSampleList(self):
        filenames = os.listdir(self.fq_dir)
        samples = set()
        for filename in filenames:
            sample_id = filename.split("_")[0]
            if self.matricespath != "":
                sample_dir = os.path.join(self.matricespath, sample_id)
                if not os.path.isdir(sample_dir):
                    samples.add(sample_id)
            else:
                samples.add(sample_id)
        self.sampleList = samples
    
    def mvMatrices(self, sample):
        if self.matricespath != "":
            mv_cmd = ["mv", f"{sample}", f"{self.matricespath}"]
            subprocess.run(mv_cmd, check=True)
            
    def cellrangerRun(self):
        # 获取文件夹中的所有文件名
        if self.sampleList == set():
            print(
                "\033[1;32m All samples have been processed with Cell Ranger\033[0m")
        else:
            print(self.sampleList)

        for sample in self.sampleList:
            subdirectory_path = os.path.join(os.getcwd(), sample)
            if os.path.exists(subdirectory_path):
                print(f"5秒钟之后删除旧文件：{subdirectory_path}")
                time.sleep(5)
                os.system(f"rm -rf {subdirectory_path}")

            cmd = f"""cellranger count --id={sample} \
    --transcriptome={self.db} \
    --fastqs={self.fq_dir} \
    --sample={sample} \
    --expect-cells={self.expectcellnum} \
    --nosecondary {self.otherItem}"""

            print("\033[1;33m Running command for sample {}:\033[0m".format(sample))
            print("\033[1;31m{}\033[0m".format(cmd))
            subprocess.run(cmd, shell=True)
            self.mvMatrices(sample)


