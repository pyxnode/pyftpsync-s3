import setuptools

with open("README.md", "rb") as fh:
    long_description = fh.read().decode()

setuptools.setup(
    name="pyftpsync-s3",
    version="0.0.9",
    author="pyxnode",
    author_email="pynode@protonmail.com",
    description="Amazon S3 synchronization target for pyftpsync library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pyxnode/pyftpsync-s3",
    packages=setuptools.find_packages(),
    install_requires=[
        'pyftpsync',
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
