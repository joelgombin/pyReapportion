from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pyreapportion",
    version="0.1.0",
    author="Joel Gombin",
    description="Reapportion data from one geography to another",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/joelgombin/pyReapportion",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "geopandas>=0.14.0",
        "shapely>=2.0.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
        ]
    },
)
