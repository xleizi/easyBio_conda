import subprocess
import os
import platform
import requests
from bs4 import BeautifulSoup
from .Utils import requestGet


class installConda:
    def __init__(self, url="https://www.anaconda.com/download") -> None:
        self.downloadPageUrl = url
        self.links = self.get_download_links()
        self.downloadLink = self.get_download_link_for_current_system()

    def getPageSoup(self) -> BeautifulSoup:
        response = requestGet(self.downloadPageUrl)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
        
    def get_download_links(self) -> list:
        print("获取下载链接~~~")
        soup = self.getPageSoup()
        links = []
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and 'Anaconda' in href:
                links.append(href)
        return links

    def get_download_link_for_current_system(self):
        # Get current operating system (e.g., Linux, Windows, Darwin)
        system = platform.system()
        # Get current system architecture (e.g., x86_64)
        architecture = platform.machine()

        # Map from Python's platform.system() results to the terms used in the Anaconda URLs
        system_map = {
            'Windows': 'Windows',
            'Darwin': 'MacOSX',
            'Linux': 'Linux'
        }

        # Create a search string based on the current system and architecture
        search_string = f'{system_map.get(system)}-{architecture}'

        # Search for the corresponding download link
        for link in self.links:
            if search_string in link:
                return link
        
        print('No suitable download link found for your system.')
        RuntimeError
        return ''

    def install_anaconda(self):
        if platform.system() != 'Linux':
            return "This script can only be used on a Linux system."

        # Download Anaconda
        subprocess.run(["wget", self.downloadLink, "-O", "anaconda.sh"])

        # Install Anaconda
        process = subprocess.Popen(["bash", "anaconda.sh", "-b", "-p", "$HOME/anaconda3"],
                                stdin=subprocess.PIPE)
        process.communicate(input=b'\n')  # Send the Enter key

        return "Anaconda installation completed."

def main():
    ic = installConda()
    print(ic.install_anaconda())

if __name__ == '__main__':
    main()
