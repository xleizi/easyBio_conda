import os
import requests
import threadpool
import math
from time import time
import urllib.parse

from .toolsUtils import getNowTime


class Download:
    def __init__(self, url: str, fileName: str = None, dirs: str = None, perPartSize: int = 1024*1024*10, threadNum: int = 5, limitTime=3000) -> None:
        """
        初始化
        @url：文件链接
        @fileName：文件名(默认从链接中获取)
        @perPartSize：单线程下载大小(默认10MB)
        @threadNum：线程数(默认5)
        @limitTime：单线程1%进度限制时间,超时重新执行该线程(ms)
        """
        self.url = url
        self.perPartSize = perPartSize
        self.threadNum = threadNum
        self.limitTime = limitTime
        if (not fileName):
            self.fileName = self.getFileName()
        else:
            self.fileName = fileName
        if (not dirs):
            self.dirs = self.getdirs()
        else:
            self.dirs = dirs
        self.markDir()

    def getFileName(self) -> str:
        """
        从链接中获取文件名
        """
        url = urllib.parse.unquote(self.url)
        return url.split("?")[0].split("/")[-1]

    def getdirs(self) -> str:
        """
        返回当前目录
        """
        return os.getcwd()

    def markDir(self) -> None:
        """
        创建缓存和保存目录
        """
        if (not os.path.isdir(f"{self.dirs}/temp")):
            os.mkdir(f"{self.dirs}/temp")
        # if (not os.path.isdir(f"{self.dirs}/download")):
        #     os.mkdir(f"{self.dirs}/download")

    def getTotalSize(self) -> int:
        """
        获取文件总大小
        """
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"}
        res = requests.head(url=self.url, headers=headers)
        if (res.status_code == 200):
            if ("Content-Length" in res.headers):
                return int(res.headers['Content-Length'])
            else:
                return None
        else:
            return None

    def preDownload(self, index: int, totalSize: int) -> int:
        """
        检查分块下载进度 返回剩余大小
        """
        fileName = f"{self.dirs}/temp/{self.fileName}_{index}"
        if (os.path.isfile(fileName)):
            stat = os.stat(fileName)
            return totalSize - stat.st_size  # 剩余大小
        else:
            return totalSize

    def download(self, index: int, start: int, end: int) -> None:
        """
        下载分块
        """
        indexTip = f"{index}/{self.partNum-1}"  # 分块位置提示
        totalSize = end-start+1  # 分块总大小
        needDownSize = self.preDownload(index, totalSize)  # 分块剩余大小

        if (needDownSize == 0):  # 分块已下载
            # print(f"[{indexTip}][{start}-{end}]下载完成")
            print(
                "\033[1;32m[{}][{}-{}] Download completed\033[0m".format(indexTip, start, end))
            return
        if (totalSize != needDownSize):  # 分块已存在,追加模式
            file = open(f"{self.dirs}/temp/{self.fileName}_{index}", mode="ba")
        else:  # 分块未存在，新建模式
            file = open(f"{self.dirs}/temp/{self.fileName}_{index}", mode="bw")

        currentSize = 0  # 已经下载大小
        progress = 0  # 下载进度

        headers = {
            "Range": f"bytes={end - needDownSize + 1}-{end}"  # 设置下载范围
        }
        req = requests.get(url=self.url, stream=True,
                           headers=headers, timeout=self.limitTime / 1000)  # 流式下载

        startTime = int(time()*1000)  # 下载开始时间
        reDownload = False  # 重新下载标志
        for content in req.iter_content(chunk_size=2048):  # 读取并保存下载数据
            if (content):
                file.write(content)
                currentSize += 2048  # 更新已下载大小
                if (currentSize < needDownSize):  # 未完成下载
                    newProgress = int(currentSize*100/needDownSize)  # 下载进度
                    if (progress != newProgress):
                        progress = newProgress
                        divTime = int(time()*1000)-startTime  # 1%进度花费时间
                        if (divTime > self.limitTime):  # 超时,重新下载
                            reDownload = True
                            # print(f"[{divTime}ms][{indexTip}][{progress}%]超时，重新下载---{getNowTime()}")
                            print("\033[1;31m[{}ms][{}][{}%] Timeout, downloading again---{}\033[0m".format(
                                divTime, indexTip, progress, getNowTime()))
                            file.close()
                            break
                        else:
                            startTime = int(time()*1000)
                            print(
                                f"[{divTime}ms][{indexTip}][{progress}%]downloading---{getNowTime()}")
        if (reDownload):
            self.download(index, start, end)
        else:
            print(f"[{indexTip}][{start}-{end}]下载完成---{getNowTime()}")

    def checkParts(self, partList: list) -> bool:
        """
        检查全部分块是否已下载
        """
        for part in partList:
            if (self.preDownload(part['index'], part['totalSize'])):
                return False
        return True

    def checkTask(self) -> bool:
        """
        检查目标文件是否已下载
        """
        fileName = f"{self.dirs}/{self.fileName}"
        return os.path.isfile(fileName)

    def mergeParts(self):
        """
        合并分块
        """
        fileName = f"{self.dirs}/{self.fileName}"
        targetFile = open(fileName, mode="bw")
        for index in range(self.partNum):
            partFile = f"{self.dirs}/temp/{self.fileName}_{index}"
            file = open(partFile, mode="br")
            targetFile.write(file.read())
            file.close()
            print(f"合并[{partFile}]成功---{getNowTime()}")
        targetFile.close()

    def deleteParts(self):
        """
        删除缓存分块
        """
        for index in range(self.partNum):
            partName = f"{self.dirs}/temp/{self.fileName}_{index}"
            if (os.path.isfile(partName)):
                os.remove(partName)
                print(f"删除[{partName}]成功---{getNowTime()}")

    def start(self):
        totalSize = self.getTotalSize()  # 文件总大小
        if (not totalSize):
            print(
                "\033[1;31mFile does not support streaming download, program exited---{}\033[0m".format(getNowTime()))
            return
        self.partNum = math.ceil((totalSize/self.perPartSize))  # 计算分块数量
        if (self.checkTask()):
            self.deleteParts()
            print(
                "\033[1;32m{} file downloaded, task exited---{}\033[0m".format(self.fileName, getNowTime()))
            return
        pool = threadpool.ThreadPool(self.threadNum)  # 创建线程池
        partList = []  # 分块列表(包含序号和大小)
        argsList = []  # 任务参数列表

        for i in range(self.partNum):  # 构建参数
            if (i+1 == self.partNum):
                args = ([i, i*self.perPartSize, totalSize-1], None)
            else:
                args = ([i, i*self.perPartSize, (i+1)*self.perPartSize-1], None)
            argsList.append(args)
            partList.append({"index": i, "totalSize": args[0][2]-args[0][1]+1})

        reqs = threadpool.makeRequests(self.download, argsList)  # 构建任务队列
        for req in reqs:  # 提交任务
            pool.putRequest(req)
        pool.wait()  # 等待线程结束

        if (self.checkParts(partList)):  # 检查分块状态
            self.mergeParts()
            self.deleteParts()
        else:
            print(
                "\033[1;31mChunk download incomplete, please rerun the program---{}\033[0m".format(getNowTime()))
