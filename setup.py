#!/usr/bin/env python
"""
Install wagtail-linkchecker using setuptools
"""

with open('README.rst', 'r') as f:
    readme = f.read()

from setuptools import find_packages, setup

setup(
    name='wagtail-linkchecker',
    version='0.5.1',
    description="A tool to assist with finding broken links on your wagtail site.",
    long_description=readme,
    author='Takeflight',
    author_email='developers@takeflight.com.au',
    url='https://github.com/takeflight/wagtail-linkchecker',

    install_requires=[
        'wagtail>=1.0',
        'requests>=2.9.1',
        'celery>=4.0,<5'
    ],
    zip_safe=False,
    license='BSD License',

    packages=find_packages(),

    include_package_data=True,
    package_data={},

    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
    ],
)
