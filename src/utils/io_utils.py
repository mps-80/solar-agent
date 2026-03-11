"""
Utility functions for input/output processing
"""

import json
import os
from typing import Dict, Any
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel, Field, validator


class EnergyData(BaseModel):
    """Energy usage data schema"""

    property_id: str
    current_energy_usage_kwh: float = Field(gt=0)
    estimated_annual_usage_kwh: float = Field(gt=0)
    annual_usage_next_25_years: list[float] = Field(min_items=25)
    system_cost: float = Field(gt=0)
    available_incentives: float = Field(ge=0)
    location: str
    system_efficiency: float = Field(default=0.95, ge=0.5, le=1.0)
    electricity_rate_per_kwh: float = Field(default=0.15, gt=0)

    @validator("annual_usage_next_25_years")
    def validate_years(cls, v):
        """Validate that we have exactly 25 years of data"""
        if len(v) != 25:
            raise ValueError("Must provide exactly 25 years of usage data")
        return v


class InputProcessor:
    """Process and validate input JSON files"""

    @staticmethod
    def load_input(file_path: str) -> EnergyData:
        """
        Load and validate input JSON file.

        Args:
            file_path: Path to input JSON file

        Returns:
            Validated EnergyData object

        Raises:
            ValueError: If file not found or invalid format
        """
        if not os.path.exists(file_path):
            raise ValueError(f"File not found: {file_path}")

        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            energy_data = EnergyData(**data)
            return energy_data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error loading input: {str(e)}")

    @staticmethod
    def calculate_annual_savings(
        usage_kwh: float,
        efficiency: float = 0.95,
        electricity_rate: float = 0.15,
    ) -> float:
        """
        Calculate estimated annual savings.

        Args:
            usage_kwh: Annual energy usage in kWh
            efficiency: System efficiency (0-1)
            electricity_rate: Rate per kWh

        Returns:
            Estimated annual savings
        """
        return usage_kwh * efficiency * electricity_rate


class OutputFormatter:
    """Format and save analysis results"""

    @staticmethod
    def save_results(
        results: Dict[str, Any],
        output_dir: str = "data/outputs",
        filename: str = None,
    ) -> str:
        """
        Save analysis results to JSON file.

        Args:
            results: Results dictionary
            output_dir: Output directory path
            filename: Optional filename (defaults to timestamp)

        Returns:
            Path to saved file
        """
        os.makedirs(output_dir, exist_ok=True)

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"roi_analysis_{timestamp}.json"

        file_path = os.path.join(output_dir, filename)

        # Convert non-serializable objects
        results_clean = json.loads(json.dumps(results, default=str))

        with open(file_path, "w") as f:
            json.dump(results_clean, f, indent=2)

        return file_path

    @staticmethod
    def format_currency(value: float) -> str:
        """Format value as currency"""
        return f"Rs. {value:,.2f}"

    @staticmethod
    def format_percentage(value: float) -> str:
        """Format value as percentage"""
        return f"{value:.2f}%"
