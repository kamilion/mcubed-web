#!/usr/bin/env python

from distutils.core import setup

setup(
    version='1.4.1',
    url='https://github.com/nathforge/pyotp',
    name='pyotp',
    description='https://github.com/nathforge/pyotp',
    author='Mark Percival (ported by Nathan Reynolds to Python)',
    author_email='nath@nreynolds.co.uk',
    packages=['pyotp'],
    package_dir={'': 'src'},
)
