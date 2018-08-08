import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="spader",
    version="0.0.1",
    author="wongherlung",
    author_email="wongherlung@gmail.com",
    description="A Single Page Application endpoint crawler.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wongherlung/spader",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
