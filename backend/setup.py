from setuptools import setup, find_packages

setup(
    name="core",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # Core dependencies will be added here
    ],
    python_requires='>=3.8',
    author="Digital Farmers",
    author_email="dev@digitalfarmers.com",
    description="Core functionality for Digital Farmers CMS",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/digitalfarmers/cms",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
