# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

try:
    long_description = open('README.rst', 'rt').read()
except IOError:
    long_description = ''

setup(
    name='linode',
    version='1.0',

    description='Linode command line interface',
    long_description=long_description,

    author='Yogesh Panchal',
    author_email='yspanchal@gmail.com',

    url='https://bitbucket.org/ypanchal/linode',
    download_url='https://bitbucket.org/ypanchal/linodei/get/master.tar.gz',

    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'requests',
        'tabulate',
    ],
    entry_points='''
        [console_scripts]
        linode=linode.main:linode
    ''',
#    classifiers=[
#        'License :: OSI Approved :: Apache Software License',
#        'Programming Language :: Python',
#    ],
)
