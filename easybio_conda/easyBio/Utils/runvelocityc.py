from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import subprocess


class runvelocityc:
    def __init__(self, matrices_file: str, rmsk_file: str, gtf_file: str, max_memory: int) -> None:
        self.matrices_file = matrices_file
        self.rmsk_file = rmsk_file
        self.gtf_file = gtf_file
        self.max_memory = max_memory

    # Function to run velocyto command for a given directory
    def run_velocyto(self, directory, num_threads):
        cmd = f'velocyto run10x -m {self.rmsk_file} {self.matrices_file}/{directory} {self.gtf_file} -@ {num_threads}'
        subprocess.run(cmd, shell=True)

    # Function to check if a directory contains any loom files
    def check_existing_loom(self, directory):
        velocyto_dir = os.path.join(directory, 'velocyto')
        if os.path.exists(velocyto_dir) and os.path.isdir(velocyto_dir):
            loom_files = [f for f in os.listdir(
                velocyto_dir) if f.endswith('.loom')]
            if len(loom_files) >= 1:
                return True
        return False

    # Function to compute the maximum number of workers for ThreadPoolExecutor
    def compute_max_workers(self):
        folders = [f for f in os.listdir(self.matrices_file) if os.path.isdir(
            os.path.join(self.matrices_file, f)) and not self.check_existing_loom(os.path.join(self.matrices_file, f))]
        folder_count = len(folders)
        max_workers = 1
        for i in range(1, min(folder_count+1, 21)):
            if folder_count % i == 0:
                max_workers = i
        return max_workers

    def buildLoomFile(self):
        # Compute the number of workers and threads for parallel execution
        max_workers = self.compute_max_workers()
        num_threads = (self.max_memory // 4) // max_workers

        # Get the list of folders to process, excluding those with existing loom files
        folders = [f for f in os.listdir(self.matrices_file) if os.path.isdir(
            os.path.join(self.matrices_file, f)) and not self.check_existing_loom(os.path.join(self.matrices_file, f))]
        print(folders)
        # Run velocyto in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
         # with ThreadPoolExecutor(max_workers=1) as executor:
            futures = {executor.submit(
                self.run_velocyto, folder, num_threads): folder for folder in folders}
            # Process the results and print the status for each folder
            for future in as_completed(futures):
                folder = futures[future]
