# -*- coding: utf-8 -*-
# Author: Lei
# Date: 2023-04-20
# Description:
import math
import os
import time
from .netUtils import requestGet
from .download import Download


def getbioproject(gsenumber):
    """
    This function retrieves the BioProject identifier for a given GSE number.
    The BioProject identifier is a unique identifier assigned to a biological project in the NCBI BioProject database.

    Arguments:
    gsenumber -- A string representing the GSE number of the GDS record for which the BioProject identifier is to be retrieved.

    Returns:
    A string representing the BioProject identifier of the corresponding biological project.
    """
    gseid = int(gsenumber.replace("GSE", "")) + 200000000
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gds&retmode=json&id={gseid}"
    re = requestGet(url)
    results = re.json()
    try:
        res = results['result']
        uids = res['uids']
    except:
        uids = []
    uid = uids[0]
    geopg = res[uid]
    bioproject = geopg["bioproject"]
    print("\033[1;32mbioproject: {}\033[0m".format(bioproject))
    return bioproject


def idDownloadAll(results, dirs):
    exitCount = sum(1 for study in results if os.path.exists(
        f"{dirs}/{study['run_accession']}.sra"))
    return exitCount == len(results)


def getProResults(gsenumber):
    bioproject = getbioproject(gsenumber)
    # bioproject = getbioproject(gsenumber)
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-TW;q=0.5,mt;q=0.4',
        'Dnt': '1',
        'Host': 'www.ebi.ac.uk',
        'Referer': f'https://www.ebi.ac.uk/ena/browser/view/{bioproject}',
        'sec-ch-ua-platform': 'Windows',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        "Sec-Fetch-Site": 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67',
        'x-requested-with': 'XMLHttpRequest'
    }
    pjurl = f"https://www.ebi.ac.uk/ena/portal/api/filereport?result=read_run&accession={bioproject}&limit=1000&format=json&fields=run_accession,sra_md5,sample_alias,submitted_md5,submitted_ftp"
    pjre = requestGet(pjurl, Headers=headers)
    # pjre = requestGet(pjurl)
    results = pjre.json()
    try:
        print(results["message"])
        print(results)
        time.sleep(60)
        getProResults(gsenumber)
    except:
        try:
            print(results[0]["run_accession"])
            return results
        except:
            print(results)
            time.sleep(60)
            getProResults(gsenumber)


def downLoadSRA(gsenumber, results, dirs, threads) -> bool:
    """
    This function downloads SRA files for a given GSE number using the EBI REST API.
    The SRA files are downloaded to the specified directory.

    Arguments:
    gsenumber -- A string representing the GSE number of the GDS record for which the SRA files are to be downloaded.
    dirs -- A string representing the directory where the SRA files are to be downloaded.
    threads -- An integer representing the number of threads to be used for downloading the SRA files.

    Returns:
    None
    """
    print("\033[1;33m{}\033[0m".format("*" * 80))   # 黄

    threads = min(50, math.ceil(threads / 2))
    filedirs = f"{dirs}/{gsenumber}/raw/sra"
    os.makedirs(filedirs, exist_ok=True)

    if idDownloadAll(results, filedirs):
        print("\033[32mAll files have been successfully downloaded. Exiting or entering the fastq-dump program...\033[0m")
        return True

    for study in results:
        run_accession = study["run_accession"]
        print("\033[33mrun_accession: {}\033[0m".format(run_accession))
        # sra_md5 = study["sra_md5"]
        sra_ftp = f"https://sra-pub-run-odp.s3.amazonaws.com/sra/{run_accession}/{run_accession}"
        download = Download(sra_ftp, dirs=filedirs, fileName=f"{run_accession}.sra",
                            threadNum=threads, limitTime=60000)
        download.start()
    return False



