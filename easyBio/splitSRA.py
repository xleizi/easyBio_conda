import argparse
import subprocess
from pathlib import Path

# Parse command line arguments
parser = argparse.ArgumentParser(
    description="Process .sra files with parallel-fastq-dump")
parser.add_argument("-f", "--folder", default=".",
                    help="Folder containing .sra files (default: current directory)")
parser.add_argument("-t", "--threads", type=int, default=8,
                    help="Number of threads (default: 8)")
parser.add_argument("-o", "--outdir", default="./",
                    help="Output directory (default: out)")

parser.add_argument("-k", "--kind", default="--split-files",
                    help="Zhe kind of split")


args = parser.parse_args()

folder = Path(args.folder)
outdir = Path(args.outdir)
threads = args.threads
kind = args.kind

# Create output directory if it doesn't exist
outdir.mkdir(parents=True, exist_ok=True)


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


            