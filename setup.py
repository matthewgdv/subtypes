from setuptools import setup, find_packages
from os import path

__version__ = "0.0.1"

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pysubtypes",
    version=__version__,
    description="Provides subclasses for common python types with additional functionality and convenience methods.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/matthewgdv/subtypes",
    license="MIT",
    classifiers=[
      "Development Status :: 3 - Alpha",
      "Intended Audience :: Developers",
      "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "aenum",
        "bs4",
        "case_conversion",
        "clipboard",
        "dateutil",
        "inflect",
        "lazy_property",
        "maybe",
        "numpy",
        "pandas",
        "regex",
        "tabulate"
    ],
    author="Matt GdV",
    author_email="matthewgdv@gmail.com"
)
