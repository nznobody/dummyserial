import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dummyserial", # Replace with your own username
    version="1.1.0",
    author="Greg Albrecht",
    copyright='Copyright 2016 Orion Labs, Inc.',
    author_email="gba@orionlabs.io",
    description="Dummy Serial Implementation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ampledata/dummyserial",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)