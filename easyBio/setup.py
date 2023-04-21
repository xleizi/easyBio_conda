from setuptools import setup, find_packages

VERSION = '0.1.0'

setup(
    name='easyBio',  # package name
    version=VERSION,  # package version
    author='Your Name',
    author_email='your-email@example.com',
    description='The purpose of the creation of this package is to make bioinformatics analysis simpler.',
    packages=find_packages(),
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'downloadSRA=your_project.downloadSRA:main',
            'splitSRA=your_project.splitSRA:main',
        ]
    },
    install_requires=[
        'biopython',
        # Add more dependencies here
    ],
)
