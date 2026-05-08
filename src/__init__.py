"""
Protein Structure/Function Analysis Package

A comprehensive Python package for analyzing protein structures,
extracting features, and predicting protein functions using machine learning.

Author: [Your Name]
Program: Masters in Bioinformatics, Saaraland
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Import main classes
from .structure_analyzer import ProteinAnalyzer, StructureComparator
from .data_fetcher import PDBFetcher, UniProtFetcher, InterProFetcher
from .feature_extractor import FeatureExtractor
from .predictor import FunctionPredictor

__all__ = [
    'ProteinAnalyzer',
    'StructureComparator',
    'PDBFetcher',
    'UniProtFetcher',
    'InterProFetcher',
    'FeatureExtractor',
    'FunctionPredictor',
]
