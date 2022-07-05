#!/usr/bin/env python

from setuptools import setup

with open("README.rst") as readme:
    long_description = readme.read()

setup(
    name='pdf417gen',
    version='0.7.1',
    description='PDF417 2D barcode generator for Python',
    long_description=long_description,
    author='Ivan Habunek',
    author_email='ivan.habunek@gmail.com',
    url='https://github.com/ihabunek/pdf417-py/',
    keywords='pdf417 2d barcode generator',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    packages=[
        'pdf417gen',
        'pdf417gen.compaction'
    ],
    python_requires=">=3.6",
    install_requires=[
        'Pillow>=3.3.0',
    ],
    entry_points={
        'console_scripts': [
            'pdf417gen=pdf417gen.console:main',
        ],
    }
)
