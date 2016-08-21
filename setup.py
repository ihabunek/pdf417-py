#!/usr/bin/env python

from setuptools import setup

long_description = """
Easily encode your data into a 2D barcode using the PDF417 format.
"""

setup(
    name='pdf417gen',
    version='0.2.0',
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
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    packages=['pdf417'],
    install_requires=[
        'Pillow>=3.0.0',
        'future'
    ]
)
