# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

VERSION = '0.3.2'

setup(
    name='easybio',  # package name
    version=VERSION,  # package version
    author='Lei Cui',
    author_email='cuilei798@qq.com',
    maintainer='Lei Cui',
    maintainer_email='cuilei798@qq.com',
    license='MIT License',
    platforms=["linux"],
    url='https://github.com/xleizi/easyBio_conda',

    description='The purpose of the creation of this package is to make bioinformatics analysis simpler.',
    long_description=open('README.md').read(),
    packages=find_packages(),
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'easyBio=easyBio.easyBio:main',
            'easydownloadSRA=easyBio.downloadSRA:main',
            'easysplitSRA=easyBio.splitSRA:main',
            'easychangeSRAName=easyBio.changeSRAName:main',
            'easycellranger=easyBio.run_cellranger:main',
            'easyscGEOpipline=easyBio.pipline:main', 
            'easyVelocyto=easyBio.runvelocyto:main',
        ]
    },
    install_requires=[
        # 'biopython',
        'threadpool',
        'requests'
        # Add more dependencies here
    ],
    package_data={
        'Utils': ['Utils/*']
    },
    classifiers=[
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    python_requires='>=3',
)
