from setuptools import setup, find_packages

from os import path

def long_description():
    """ Read the descrption from README. """
    here = path.abspath(path.dirname(__file__))
    with open(path.join(here, "README.rst")) as f:
        return f.read()

setup(
    name="mofloc",
    version="0.0.1",
    package_dir={"": "src"},
    packages=find_packages("src"),

    author="Michail Pevnev",
    author_email="mpevnev@gmail.com",
    description="Modular Flow Control",
    long_description=long_description(),
    license="LGPL-3",
    keywords="flow control",
    url="https://github.com/mpevnev/mofloc",

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)"
        ]
)
