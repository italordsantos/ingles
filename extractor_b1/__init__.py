"""
🚀 EXTRACTOR B1 - PROCESSADOR DE MATERIAIS CAMBRIDGE
Sistema completo de extração, processamento e exportação de materiais de inglês
"""

__version__ = "1.0.0"
__author__ = "Extractor B1 Team"
__description__ = "Sistema de extração e processamento de materiais Cambridge para plataforma de inglês"

from .scripts.extractor import DocumentExtractor
from .scripts.processor import DataProcessor
from .scripts.validator import DataValidator
from .scripts.exporter import DataExporter
from .utils.config import Config
from .utils.logger import setup_logger

__all__ = [
    "DocumentExtractor",
    "DataProcessor", 
    "DataValidator",
    "DataExporter",
    "Config",
    "setup_logger"
]
