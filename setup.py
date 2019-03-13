from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='bcl2fq-local',
    version='0.1.2',
    url='https://github.com/seahurt/bcl2fq-local',
    license='MIT',
    author='Wang Jianghao',
    author_email='haozi.vv@gmail.com',
    description='Bcl2fastq wrapper',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        'xmltodict',
    ],
    entry_points={
        "console_scripts": [
            'bcl2fq-local = bcl2fq.bcl2fq:main'
        ]
    },
    platforms=['CentOS 7.0+'],
    data_files=[('bin', ['bin/bcl2fastq'])],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: POSIX :: Linux',
        "License :: OSI Approved :: MIT License",
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ]
)
