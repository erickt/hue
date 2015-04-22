
from setuptools import setup, find_packages
import pydoc, inspect
import nosetty
description, long_description = pydoc.splitdoc(inspect.getdoc(nosetty))

setup(
    name='nosetty',
    version=nosetty.__version__,
    url="http://code.google.com/p/nosetty/",
    zip_safe=False,
    author="Kumar McMillan",
    author_email = "kumar dot mcmillan / gmail.com",
    description = description,
    long_description = long_description,
    install_requires='nose',
    license = 'GNU LGPL',
    packages = find_packages(),
    keywords = 'test unittest nose nosetests plugin',
    entry_points = {
        'nose.plugins': ['tty = nosetty:NoseTTY'],
    },
)

