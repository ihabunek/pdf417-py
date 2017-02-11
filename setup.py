#!/usr/bin/env python

from setuptools import setup

with open("README.rst") as readme:
    long_description = readme.read()

setup(
    name='pdf417gen',
    version='0.5.0',
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
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    packages=['pdf417gen'],
    install_requires=[
        'Pillow>=2.0.0',
        'future'
    ]
)
