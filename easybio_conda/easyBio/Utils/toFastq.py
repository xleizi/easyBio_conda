from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import re
import subprocess


class toFastq:
    def __init__(self, dataDir: str, type="sra", FastqDir="./fq", threads=16) -> None:
        if type != "sra" and type != "bam":
            print("type only can be sra or bam")
            exit()
        self.type = type
        self.dataDir = dataDir
        self.FastqDir = FastqDir
        self.threads = threads
        self.makFastqdirs()

    def makFastqdirs(self):
        os.makedirs(self.FastqDir, exist_ok=True)
        
    def maktoFastqdirs(self):
        os.makedirs(self.toFastqDir, exist_ok=True)
        
    def check_file_exists(self, target_suffix="S1_L001_R1_001.fastq.gz"):
        for file_name in os.listdir(self.FastqDir):
            if file_name.endswith(target_suffix):
                return True
        return False

    def SRAtoFastq(self, kind):
        if self.check_file_exists():
            print(f"fastq文件已进行改名")
        else:
            self.StF(kind)
            print("\033[1;33m{}\033[0m".format("*" * 80))   # 黄
    
    def BAMtoFastq(self, tofqPath):
        self.toFastqDir = tofqPath
        self.maktoFastqdirs()
        if self.check_file_exists():
            print(f"fastq文件已进行改名")
        else:
            self.BtF(self.dataDir, tofqPath)
            self.mvtoFastq(tofqPath)
            print("\033[1;33m{}\033[0m".format("*" * 80))   # 黄
            
    def mvtoFastq(self, tofqPath):
        if not tofqPath.endswith("/"):
            tofqPath = tofqPath + "/"
        for filepath, dirnames, filenames in os.walk(tofqPath):
            for filename in filenames:
                filedir = os.path.join(filepath, filename)
                sampleid = filedir.split(tofqPath)[1].split("/")[0]
                sampleid = os.path.split(filedir)[0].split("/")
                sampleid = sampleid[len(sampleid)-2]
                sampleid = sampleid.replace("_", "-")
                fileName = os.path.split(filedir)[1].split("_")
                fileName[0] = sampleid
                fileName = "_".join(fileName)
                fileName = os.path.join(self.FastqDir, fileName)
                print(filedir, " to ", fileName)
                os.renames(filedir, fileName)
        

    def BamfastqExist(self, tofqPath, simpleName):
        sampletofqPath = os.path.join(tofqPath, simpleName)
        if os.path.exists(sampletofqPath):
            finalDir = os.path.join(sampletofqPath, os.listdir(sampletofqPath)[0])
            return os.listdir(finalDir)[0].endswith(".fastq.gz")
            # if os.listdir(finalDir)[0].endswith(".fastq.gz"):
            #     return True
            # else:
            #     os.remove(sampletofqPath)
            #     return False
        else:
            return False
    
    def BtF(self, bamfolder, tofqPath):
        bam_files = [f for f in os.listdir(bamfolder) if f.endswith('.bam')]
        sampleList = []
        for bam_file in bam_files:
            # print(bam_file)
            simpleName = bam_file.replace(".bam", "")
            if self.BamfastqExist(tofqPath, simpleName):
                print(f"Skipping {simpleName} as output files already exist.")
                continue
            sampleList.append(bam_file)

        for bam_file in sampleList:
            print(f"Processing {bam_file}...")
            samplepath = os.path.join(bamfolder, bam_file)
            sampletofqPath = os.path.join(tofqPath, simpleName)
        
        # 经测试，大概运行一个bamtofastq会使用不到3个核，所以此处最大线程设置为总线程数除以3
        with ThreadPoolExecutor(max_workers=self.threads/3) as executor:
                     # with ThreadPoolExecutor(max_workers=1) as executor:
            futures = {executor.submit(
                self.run_bamtofastq, 
                os.path.join(bamfolder, bam_file), 
                os.path.join(tofqPath, bam_file.replace(".bam", "")),
                bam_file.replace(".bam", "")): bam_file for bam_file in sampleList}
            # Process the results and print the status for each folder
            for future in as_completed(futures):
                bam_file = futures[future]

    def run_bamtofastq(self, samplepath, sampletofqPath, simpleName):
        cmd = f"""cellranger bamtofastq --traceback {samplepath} {sampletofqPath}"""
        # cmd = f"""cellranger bamtofastq --nthreads={self.threads} --traceback {samplepath} {sampletofqPath}"""
        print("\033[1;33m Running command for sample {}:\033[0m".format(simpleName))
        print("\033[1;31m{}\033[0m".format(cmd))
        subprocess.run(cmd, shell=True)
    
    def StF(self, kind):
        # Get a list of .sra files in the folder
        sra_files = [f for f in os.listdir(self.dataDir) if f.endswith('.sra')]
        # Iterate over .sra files in the folder and run the provided command
        for sra_file in sra_files:
            sra_base, _ = os.path.splitext(sra_file)

            output_files = [f for f in os.listdir(self.FastqDir) if f.startswith(
                f"{sra_base}_") and f.endswith(".fastq.gz")]

            if output_files:
                print(f"Skipping {sra_file} as output files already exist.")
                continue

            print(f"Processing {sra_file}...")

            cmd = [
                "parallel-fastq-dump",
                "--sra-id", os.path.join(self.dataDir, sra_file),
                "--threads", str(self.threads),
                "--outdir", self.FastqDir,
                kind,
                "--gzip"
            ]

            subprocess.run(cmd, check=True)
            print("\033[1;32m Finished processing", sra_file, "\033[0m")
        print("\033[1;32m All files processed.\033[0m")
    
    def count_srr_occurrences(self, folder_path):
        files = os.listdir(folder_path)
        srr_counts = defaultdict(int)
        for file in files:
            srr_match = re.match(r'(SRR\d+)_(\d)', file)
            if srr_match:
                srr = srr_match.group(1)
                srr_counts[srr] += 1
        return files, srr_counts

    def renameFQfiles(self, mapping, folder_path):
        files, srr_counts = self.count_srr_occurrences(folder_path)
        self.rename_fqfiles(files, folder_path, mapping, srr_counts)
    
    def rename_fqfiles(self, files, folder_path, mapping, srr_counts):
        name_add_mapping = {}
        name_add_srr_mapping = {}
        for file in files:
            srr_match = re.match(r'(SRR\d+)_(\d)', file)
            if srr_match:
                srr, number = srr_match.groups()
                name = mapping[srr]
                read_type = ''
                if srr_counts[srr] == 2:
                    read_type = 'R1' if number == '1' else 'R2'
                elif srr_counts[srr] == 3:
                    read_type = 'I1' if number == '1' else (
                        'R1' if number == '2' else 'R2')
                elif srr_counts[srr] == 4:
                    read_type = 'I1' if number == '1' else (
                        'I2' if number == '2' else ('R1' if number == '3' else 'R2'))

                if srr in name_add_srr_mapping:
                    lane_number = name_add_srr_mapping[srr]
                else:
                    name_add_mapping[name] = name_add_mapping.get(name, 0) + 1
                    name_add_srr_mapping[srr] = name_add_mapping[name]
                    lane_number = name_add_srr_mapping[srr]

                new_name = f"{name}_S{lane_number}_L001_{read_type}_001.fastq.gz"
                os.rename(os.path.join(folder_path, file),
                        os.path.join(folder_path, new_name))
                print(f'Renamed {file} to {new_name}')
