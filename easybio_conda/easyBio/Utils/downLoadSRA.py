import math
import os
from .download import Download
from .toolsUtils import sraMd5Cal

class downLoadSRA:
    def __init__(self, results, rawdirs: str, threads=16, sraDir="sra") -> None:
        self.results = results
        self.rawdirs = rawdirs
        self.threads = threads
        self.srafolder = f"{rawdirs}/{sraDir}"
        self.maksradirs()
        self.addSRAName()
        self.getmd5Map()
        self.getSample_aliasList()
        # print(self.isDownloadAll())
        # self.DownloadBam()

    def addSRAName(self):
        newList = []
        for result in self.results:
            sraName = f'{result["run_accession"]}.sra'
            result["sraName"] = sraName
            newList.append(result)
        self.results = newList

    def maksradirs(self):
        os.makedirs(self.srafolder, exist_ok=True)

    def getmd5Map(self):
        self.md5List = {}
        for result in self.results:
            sra_md5 = result["sra_md5"]
            if sra_md5 != "":
                self.md5List[result["sraName"]] = sra_md5
        print(self.md5List)
        return self.md5List
    
    def getSample_aliasList(self):
        sample_aliasList = {}
        for result in self.results:
            sample_aliasList[result["sraName"]] = result["sample_alias"]
        self.sampleMap = sample_aliasList
        return self.sampleMap
    
    def isDownloadAll(self):
        exitCount = sum(1 for study in self.results if os.path.exists(
            f"{self.srafolder}/{study['run_accession']}.sra"))
        return exitCount == len(self.results)

    def calThreads(self) -> int:
        self.threads = min(50, math.ceil(self.threads / 2))
        return self.threads

    def Download(self):
        reDownloadSra = [1, 2, 3]
        while len(reDownloadSra) > 1:
            check = False
            while not check:
                # print(results)
                check = self.DLBAM()
            reDownloadSra = sraMd5Cal(
                self.srafolder, self.md5List, self.rawdirs)
        print("\033[1;33m{}\033[0m".format("*" * 80))   # 黄

    def DLBAM(self) -> bool:
        print("\033[1;33m{}\033[0m".format("*" * 80))   # 黄

        if self.isDownloadAll():
            print("\033[32mAll files have been successfully downloaded. Exiting or entering the fastq-dump program...\033[0m")
            return True

        for study in self.results:
            run_accession = study["run_accession"]
            print("\033[33mrun_accession: {}\033[0m".format(run_accession))
            # sra_md5 = study["sra_md5"]
            bam_ftp = f"https://sra-pub-run-odp.s3.amazonaws.com/sra/{run_accession}/{run_accession}"
            print(bam_ftp)
            download = Download(bam_ftp, dirs=self.srafolder, fileName=f"{run_accession}.sra",
                                threadNum=self.threads, limitTime=60000)
            download.start()

        return False
