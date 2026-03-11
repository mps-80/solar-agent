"""
Configuration settings for the application
"""

from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration class for Solar ROI Calculator"""

    # API Configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")

    # RAG Configuration
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 100
    TOP_K_RESULTS: int = 3

    # LLM Configuration
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 2048

    # ROI Calculation
    DEFAULT_DEGRADATION_RATE: float = 0.005  # 0.5% annual
    DEFAULT_INFLATION_RATE: float = 0.03  # 3% annual
    ANALYSIS_PERIOD_YEARS: int = 25

    # File Paths
    POLICY_DIR: str = "data/policies"
    INPUT_DIR: str = "data/inputs"
    OUTPUT_DIR: str = "data/outputs"

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = "solar_roi.log"


def get_config() -> Config:
    """Get configuration instance"""
    return Config
