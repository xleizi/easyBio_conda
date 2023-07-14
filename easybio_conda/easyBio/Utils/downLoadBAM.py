import math
import os
from .download import Download
from .toolsUtils import sraMd5Cal

class downLoadBAM:
    def __init__(self, results, rawdirs: str, threads=16, bamDir="bam") -> None:
        self.results = results
        self.rawdirs = rawdirs
        self.threads = threads
        self.bamfolder = f"{rawdirs}/{bamDir}"
        self.makbamdirs()
        self.addBamName()
        self.getmd5Map()
        # print(self.isDownloadAll())
        # self.Download()

    def addBamName(self):
        newList = []
        for result in self.results:
            bamName = result["submitted_ftp"].split(";")[0].split("/")
            bamName = bamName[len(bamName)-1]
            result["bamName"] = bamName
            newList.append(result)
        self.results = newList

    def makbamdirs(self):
        os.makedirs(self.bamfolder, exist_ok=True)

    def getmd5Map(self):
        self.md5List = {}
        for result in self.results:
            bammd5 = result["submitted_md5"].split(";")[0]
            self.md5List[result["bamName"]] = bammd5
        print(self.md5List)
        return self.md5List

    def isDownloadAll(self):
        exitCount = sum(1 for study in self.results if os.path.exists(
            f"{self.bamfolder}/{study['bamName']}"))
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
                self.bamfolder, self.md5List, self.rawdirs)
        print("\033[1;33m{}\033[0m".format("*" * 80))   # 黄

    def DLBAM(self) -> bool:
        print("\033[1;33m{}\033[0m".format("*" * 80))   # 黄

        if self.isDownloadAll():
            print("\033[32mAll files have been successfully downloaded. Exiting or entering the fastq-dump program...\033[0m")
            return True

        for study in self.results:
            bamName = study["bamName"]
            run_accession = study["run_accession"]
            print("\033[33mrun_accession: {}\033[0m".format(run_accession))
            # sra_md5 = study["sra_md5"]
            downloadStu = False
            srcCount = 0
            while not downloadStu:
                srcCount += 1
                bam_ftp = f"https://sra-pub-src-{srcCount}.s3.amazonaws.com/{run_accession}/{bamName}.1"
                print(bam_ftp)
                download = Download(bam_ftp, dirs=self.bamfolder, fileName=f"{bamName}",
                                    threadNum=self.threads, limitTime=60000)
                downloadStu = download.start() if srcCount < 10 else True
        return False
