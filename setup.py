import os
from setuptools import setup, find_packages

# Safely read the README file if it exists
long_description = ''
if os.path.exists('README.md'):
    with open('README.md', 'r', encoding='utf-8') as fh:
        long_description = fh.read()

setup(
    name="capm-metrics",
    version="0.1.0",
    author="Cheng Shi",  # Replace with your actual name
    author_email="mr.cheng.shi@gmail.com",
    description="A stock performance tool based on the CAPM model",
    long_description=long_description,  # Load README.md content
    long_description_content_type="text/markdown",
    url="https://github.com/C-Shi/capm_metrics",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    install_requires=[
        'numpy',
        'pandas',
        'yfinance',
    ],
    license="MIT",
    keywords="CAPM stock analysis finance",
    project_urls={
        "Bug Tracker": "https://github.com/C-Shi/capm_metrics/issues",
        "Documentation": "https://github.com/C-Shi/capm_metrics#readme",
    },
    tests_require=[
        'pytest',
    ],
)
