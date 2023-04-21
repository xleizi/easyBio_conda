import subprocess


def splitSRAfun(folder, outdir, threads, kind):
    # Iterate over .sra files in the folder and run the provided command
    for sra_file in folder.glob("*.sra"):
        sra_base = sra_file.stem

        # Check if output files already exist
        output_files = list(outdir.glob(f"{sra_base}_*.fastq.gz"))

        if output_files:
            print(f"Skipping {sra_file} as output files already exist.")
            continue

        print(f"Processing {sra_file}...")

        cmd = [
            "parallel-fastq-dump",
            "--sra-id", str(sra_file),
            "--threads", str(threads),
            "--outdir", str(outdir),
            kind,
            "--gzip"
        ]

        subprocess.run(cmd, check=True)
        print(f"Finished processing {sra_file}")

    print("All files processed.")
