from setuptools import setup, find_packages

setup(
    name="data-path-config",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "python-dotenv>=0.19.0"
    ],
    author="guocity",
    author_email="",  # Add your email
    description="A utility for managing data and log directory paths in Python projects",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/guocity/data-path-config",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
