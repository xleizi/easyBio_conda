# -*- coding: utf-8 -*-
# Author: Lei
# Date: 2023-04-20
# Description:
import math
import os
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
    pjurl = f"https://www.ebi.ac.uk/ena/portal/api/filereport?result=read_run&accession={bioproject}&limit=1000&format=json&fields=run_accession,sra_md5"
    pjre = requestGet(pjurl)
    results = pjre.json()
    return results


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

