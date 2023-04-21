import math
from Utils.netUtils import requestGet
from Utils.download import Download
from Utils.toolsUtils import createDir


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


def downLoadSRA(gsenumber, dirs, threads):
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
    threads = min(50, math.ceil(threads / 2))

    print("\033[1;33m{}\033[0m".format("*" * 80))   # 黄

    bioproject = getbioproject(gsenumber)

    pjurl = f"https://www.ebi.ac.uk/ena/portal/api/filereport?result=read_run&accession={bioproject}&offset=0&limit=1000&format=json&fields=study_accession,secondary_study_accession,sample_accession,secondary_sample_accession,experiment_accession,run_accession,submission_accession,tax_id,scientific_name,instrument_platform,instrument_model,library_name,nominal_length,library_layout,library_strategy,library_source,library_selection,read_count,base_count,center_name,first_public,last_updated,experiment_title,study_title,study_alias,experiment_alias,run_alias,fastq_bytes,fastq_md5,fastq_ftp,fastq_aspera,fastq_galaxy,submitted_bytes,submitted_md5,submitted_ftp,submitted_aspera,submitted_galaxy,submitted_format,sra_bytes,sra_md5,sra_ftp,sra_aspera,sra_galaxy,cram_index_ftp,cram_index_aspera,cram_index_galaxy,sample_alias,broker_name,sample_title,nominal_sdev,first_created"
    pjre = requestGet(pjurl)
    results = pjre.json()
    for study in results:
        run_accession = study["run_accession"]
        print("\033[33mrun_accession: {}\033[0m".format(run_accession))
        filedirs = f"{dirs}/{gsenumber}/raw/sra"
        createDir(filedirs)
        # sra_md5 = study["sra_md5"]
        sra_ftp = f"https://sra-pub-run-odp.s3.amazonaws.com/sra/{run_accession}/{run_accession}"
        download = Download(sra_ftp, dirs=filedirs, fileName=f"{run_accession}.sra",
                            threadNum=threads, limitTime=60000)
        download.start()
