from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="protein-structure-analysis",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A research project for protein structure and function analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/protein-structure-analysis",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Development Status :: 3 - Alpha",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scipy>=1.7.0",
        "scikit-learn>=1.0.0",
        "biopython>=1.79",
        #"prody>=2.1.0",
        "xgboost>=1.5.0",
        "joblib>=1.1.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        #"plotly>=5.0.0",
        "requests>=2.26.0",
        "pyyaml>=5.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "pytest-cov>=2.12.0",
            "black>=21.7b0",
            "flake8>=3.9.0",
            "isort>=5.9.0",
        ],
        "notebook": [
            "jupyter>=1.0.0",
            "jupyterlab>=3.0.0",
            "ipython>=7.0.0",
        ],
        "all": [
            "pytest>=6.2.0",
            "jupyter>=1.0.0",
            "jupyterlab>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "protein-analysis=src.cli:main",
        ],
    },
)
