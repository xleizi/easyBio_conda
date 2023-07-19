# -*- coding: utf-8 -*-
# Author: Lei
# Date: 2023-06-08
# Description:
from collections import defaultdict
import os
import re
import shutil
import subprocess
import threading

import pandas as pd

from .toolsUtils import sraMd5Cal
from .download import Download
from .netUtils import requestGet
from .easyCellranger import easyCellranger

class gsaProject:
    def __init__(self, inputName: str, dirs_path="./") -> None:
        if inputName.startswith("PRJCA"):
            pjurl = f"https://ngdc.cncb.ac.cn/gsa-human/hra/getAjax/searchByPrjAccession?prjAccession={inputName}"
            hra = requestGet(pjurl).json()["listHras"][0]["accession"]
        elif inputName.startswith("HRA"):
            hra = inputName
        self.hra = hra
        self.getStudyId()
        # self.readExcel()
        # self.getAccList()
        print("hra:", hra)
        self.dirs_path = f"{dirs_path}/{inputName}"
        self.raw_path = f"{self.dirs_path}/raw"
        self.fq_path = f"{self.raw_path}/fq"
        self.fq_path2 = f"{self.raw_path}/fq2"
        if self.raw_path == "":
            self.excel_path = f"{self.hra}.xlsx"
        else:
            self.excel_path = f"{self.raw_path}/{self.hra}.xlsx"
        os.makedirs(self.dirs_path, exist_ok=True)
        os.makedirs(self.raw_path, exist_ok=True)
        os.makedirs(self.fq_path, exist_ok=True)
        os.makedirs(self.fq_path2, exist_ok=True)

    def printPro(self) -> None:
        print(self.hra)

    def getStudyId(self) -> str:
        hraurl = f"https://ngdc.cncb.ac.cn/gsa-human/ajaxb/runinstudy?accession={self.hra}&pageSize=10"
        self.studyId = requestGet(hraurl).json()["runViews"][0]["studyId"]
        return self.studyId

    def downLoadRunExcel(self) -> None:
        exurl = f"https://ngdc.cncb.ac.cn/gsa-human/file/exportExcelFile?fileName=/webdb/gsagroup/webApplications/gsa_human_20200410/gsa-human/batchExcel/human/{self.hra}/{self.hra}.xlsx&study_id={self.studyId}&requestFlag=0"
        response = requestGet(exurl)
        with open(self.excel_path, 'wb') as file:
            file.write(response.content)

    def checkExcel(self) -> None:
        if not os.path.exists(self.excel_path):
            self.downLoadRunExcel()

    def readExcel(self) -> pd.DataFrame:
        self.checkExcel()
        self.exceldf = pd.read_excel(self.excel_path, sheet_name='Run')

    def checkDataFrame(self) -> None:
        if not hasattr(self, 'exceldf'):
            self.readExcel()

    def checkmd5Map(self) -> None:
        if not hasattr(self, 'md5List'):
            self.getMd5List()

    def checkfileLinkList(self) -> None:
        if not hasattr(self, 'fileLinkList'):
            self.getFileLinkList()

    def getAccList(self) -> list:
        self.checkDataFrame()
        df = self.exceldf
        AccList = []
        for i in range(len(df)):
            AccList.append(df.iloc[i, 0])
        self.accList = AccList
        return self.accList

    def getMd5List(self) -> map:
        self.checkDataFrame()
        df = self.exceldf
        md5List = {}
        for i in range(len(df)):
            file = df.iloc[i, 4]
            sra_md5 = df.iloc[i, 5]
            md5List[file] = sra_md5
            file = df.iloc[i, 7]
            sra_md5 = df.iloc[i, 8]
            md5List[file] = sra_md5
        self.md5List = md5List
        return self.md5List

    def getFileList(self) -> str:
        self.checkmd5Map()
        fileList = self.md5List.keys()
        self.fileList = fileList
        return self.fileList

    def getFileLinkList(self) -> str:
        self.checkDataFrame()
        df = self.exceldf
        FileLinkList = []
        for i in range(len(df)):
            FileLinkList.append(df.iloc[i, 6])
            FileLinkList.append(df.iloc[i, 9])
        self.fileLinkList = FileLinkList
        return self.fileLinkList

    def downloadCheck(self) -> bool:
        items = os.listdir(self.fq_path)
        fileList = []
        for item in items:
            item_path = os.path.join(self.fq_path, item)
            if os.path.isfile(item_path):
                fileList.append(item)
        return len(fileList) == len(self.fileLinkList)

    def downloadFiles(self, threads=16, copy=False) -> None:
        if self.check_fqfile_exists('S1_L001_R1_001.fastq.gz'):
            print(f"fastq文件已进行改名")
        else:
            self.checkfileLinkList()
            neededDown = self.fileMd5Check()
            while len(neededDown) > 0:
                check = self.downloadCheck()
                while not check:
                    for FileLink in self.fileLinkList:
                        fileurl = f"https://download.cncb{FileLink[18:]}"
                        items = FileLink.split("/")
                        fileName = items[len(items)-1]
                        download = Download(fileurl, dirs=self.fq_path, fileName=fileName,
                                            threadNum=threads, limitTime=60000)
                        download.start()
                    check = self.downloadCheck()
                neededDown = self.fileMd5Check()
            try:
                shutil.rmtree(f"{self.fq_path}/temp")
            except:
                pass
            if copy:
                self.cpfqFiles(threads)
            
    def fileMd5Check(self) -> list:
        self.checkmd5Map()
        return sraMd5Cal(self.fq_path, self.md5List, self.raw_path)
    
    def getFileMapping(self) -> map:
        self.checkDataFrame()
        df = self.exceldf
        FileMapping = {}
        for i in range(len(df)):
            FileMapping[df.iloc[i, 0]] = df.iloc[i, 2]
        self.FileMapping = FileMapping
        return self.FileMapping
    
    def cpfqFiles(self, threadsNum=16) -> None:
        print(f"threadsNum: {threadsNum}")
        files = os.listdir(self.fq_path)
        
        semaphore = threading.Semaphore(threadsNum)

        def copy_file(fq_file, fq_file2):
            semaphore.acquire()
            try:
                if not os.path.exists(fq_file2):
                    shutil.copy2(fq_file, fq_file2)
                    print(f"{fq_file}: 已复制")
                else:
                    print(f"{fq_file}: 已复制")
            finally:
                semaphore.release()

        threads = []
        for file in files:
            fq_file = os.path.join(self.fq_path, file)
            fq_file2 = os.path.join(self.fq_path2, file)
            thread = threading.Thread(
                target=copy_file, args=(fq_file, fq_file2))
            thread.start()
            threads.append(thread)

        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
    def count_hrr_occurrences_fq(self, folder_path = ""):
        if folder_path == "":
            files = os.listdir(self.fq_path)
        else:
            files = os.listdir(folder_path)
        srr_counts = defaultdict(int)
        for file in files:
            srr_match = re.match(r'(HRR\d+)_[fr](\d)', file)
            if srr_match:
                srr = srr_match.group(1)
                srr_counts[srr] += 1
        return files, srr_counts

    def rename_files(self, mapping, files, srr_counts, folder_path = ""):
        if folder_path == "":
            folder_path = self.fq_path
        name_add_mapping = {}
        name_add_srr_mapping = {}
        for file in files:
            srr_match = re.match(r'(HRR\d+)_[fr](\d)', file)
            if srr_match:
                srr, number = srr_match.groups()
                name = mapping[srr]
                read_type = ''
                if srr_counts[srr] == 2:
                    read_type = 'R1' if number == '1' else 'R2'
                elif srr_counts[srr] == 3:
                    read_type = 'I1' if number == '1' else (
                        'R1' if number == '2' else 'R2')

                if srr in name_add_srr_mapping:
                    lane_number = name_add_srr_mapping[srr]
                else:
                    name_add_mapping[name] = name_add_mapping.get(name, 0) + 1
                    name_add_srr_mapping[srr] = name_add_mapping[name]
                    lane_number = name_add_srr_mapping[srr]

                lane_number_str = ""
                if lane_number < 10:
                    lane_number_str = f"00{lane_number}"
                elif lane_number < 100:
                    lane_number_str = f"0{lane_number}"
                else:
                    lane_number_str = f"{lane_number}"

                new_name = f"{name}_S1_L{lane_number_str}_{read_type}_001.fastq.gz"
                os.rename(os.path.join(folder_path, file),os.path.join(folder_path, new_name))
                print(f'Renamed {file} to {new_name}')

    def check_fqfile_exists(self, target_suffix='S1_L001_R1_001.fastq.gz') -> bool:
        for file_name in os.listdir(self.fq_path):
            if file_name.endswith(target_suffix):
                return True
        return False

    def renamegsa(self, folder_path=""):
        if folder_path == "":
            folder_path = self.fq_path
            
        if self.check_fqfile_exists('S1_L001_R1_001.fastq.gz'):
            print(f"fastq文件已进行改名")
        else:
            files, srr_counts = self.count_hrr_occurrences_fq(folder_path)
            self.rename_files(self.getFileMapping(), files,
                              srr_counts, folder_path)
            print("\033[1;32m Rename completed\033[0m")
    
    def cellrangerRun(self, db, expectcellnum = 3000, fq_dir = "", otherItem="", matricespath=""):
        if matricespath == "":
            matricespath = f"{self.raw_path}/matrices"
            
        if fq_dir == "":
            # 获取文件夹中的所有文件名
            fq_dir = self.fq_path

        ec = easyCellranger(fq_dir, expectcellnum,
                            db, otherItem, matricespath)
        ec.cellrangerRun()
        
        # if fq_dir == "":
        #     # 获取文件夹中的所有文件名
        #     fq_dir = self.fq_path
        #     filenames = os.listdir(self.fq_path)
        
    #     current_dir = os.getcwd()
    #     # 获取目录中所有的子目录
    #     subdirectories = [d for d in os.listdir(
    #         current_dir) if os.path.isdir(os.path.join(current_dir, d))]

    #     # 遍历子目录，检查是否以“SRR”开头
    #     for subdirectory in subdirectories:
    #         if subdirectory.startswith("HRX"):
    #             print("\033[1;31m Found residual folder, removing it...\033[0m")
    #             # 如果以“HRX”开头，则删除这个子目录及其内容
    #             subdirectory_path = os.path.join(current_dir, subdirectory)
    #             if subdirectory_path != "":
    #                 # rm -rf删的更快(*^▽^*)
    #                 os.system(f"rm -rf {subdirectory_path}")

    #     # time.sleep(10000)
    #     samples = set()
    #     for filename in filenames:
    #         if filename.startswith("HRX"):
    #             sample_id = filename.split("_")[0]
    #             # 剔除掉已存在的处理好的文件夹
    #             if matricespath != "":
    #                 sample_dir = os.path.join(matricespath, sample_id)
    #                 if not os.path.isdir(sample_dir):
    #                     samples.add(sample_id)

    #     if samples == set():
    #         print("\033[1;32m All samples have been processed with Cell Ranger\033[0m")
    #     else:
    #         print(samples)

    #     for sample in samples:
    #         cmd = f"""cellranger count --id={sample} \
    # --transcriptome={db} \
    # --fastqs={fq_dir} \
    # --sample={sample} \
    # --expect-cells={expectcellnum} \
    # --nosecondary {otherItem}"""

    #         print("\033[1;33m Running command for sample {}:\033[0m".format(sample))
    #         print("\033[1;31m{}\033[0m".format(cmd))
    #         subprocess.run(cmd, shell=True)

    #         if matricespath != "":
    #             mv_cmd = ["mv", f"{sample}", f"{matricespath}"]
    #             subprocess.run(mv_cmd, check=True)
    
        

