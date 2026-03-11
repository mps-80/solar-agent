"""
ROI calculation logic for solar systems
"""

from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
import math


@dataclass
class ROIResult:
    """ROI calculation result"""
    initial_investment: float
    net_investment: float
    annual_savings: float
    breakeven_months: float
    breakeven_years: float
    roi_percentage_5yr: float
    roi_percentage_10yr: float
    roi_percentage_25yr: float
    cumulative_savings_25yr: float
    yearly_breakdown: List[Dict]


class ROICalculator:
    """Calculate ROI for solar energy systems"""

    def __init__(
        self,
        system_cost: float,
        available_incentives: float = 0,
        annual_savings: float = 0,
        degradation_rate: float = 0.005,  # 0.5% annual degradation
        inflation_rate: float = 0.03,  # 3% annual inflation
    ):
        """
        Initialize ROI calculator.

        Args:
            system_cost: Total cost of solar system
            available_incentives: Available tax credits/rebates
            annual_savings: Estimated annual energy savings
            degradation_rate: Panel degradation rate per year
            inflation_rate: Inflation rate for future savings
        """
        self.system_cost = system_cost
        self.available_incentives = available_incentives
        self.annual_savings = annual_savings
        self.degradation_rate = degradation_rate
        self.inflation_rate = inflation_rate
        self.net_investment = system_cost - available_incentives

    def calculate_roi(self) -> ROIResult:
        """
        Calculate complete ROI metrics.

        Returns:
            ROIResult object with all calculations
        """
        # Calculate breakeven
        breakeven_months = self._calculate_breakeven()

        # Calculate ROI at different time periods
        roi_5yr = self._calculate_roi_at_years(5)
        roi_10yr = self._calculate_roi_at_years(10)
        roi_25yr = self._calculate_roi_at_years(25)

        # Calculate 25-year cumulative savings
        total_25yr = self._calculate_cumulative_savings(25)

        # Generate yearly breakdown
        yearly_breakdown = self._generate_yearly_breakdown(25)

        return ROIResult(
            initial_investment=self.system_cost,
            net_investment=self.net_investment,
            annual_savings=self.annual_savings,
            breakeven_months=breakeven_months,
            breakeven_years=breakeven_months / 12,
            roi_percentage_5yr=roi_5yr,
            roi_percentage_10yr=roi_10yr,
            roi_percentage_25yr=roi_25yr,
            cumulative_savings_25yr=total_25yr,
            yearly_breakdown=yearly_breakdown,
        )

    def _calculate_breakeven(self) -> float:
        """
        Calculate breakeven period in months.

        Returns:
            Breakeven period in months
        """
        if self.annual_savings <= 0:
            return float('inf')

        # Monthly savings (accounting for degradation on average)
        monthly_rate = 1 - (self.degradation_rate / 12)
        monthly_savings = self.annual_savings / 12

        total = 0
        months = 0

        while total < self.net_investment and months < 600:  # Cap at 50 years
            total += monthly_savings * (monthly_rate ** months)
            months += 1

        return months

    def _calculate_roi_at_years(self, years: int) -> float:
        """
        Calculate ROI percentage at specific year.

        Args:
            years: Number of years for calculation

        Returns:
            ROI percentage
        """
        cumulative_savings = self._calculate_cumulative_savings(years)
        roi = ((cumulative_savings - self.net_investment) / self.net_investment) * 100
        return max(roi, 0)  # Return 0 if negative

    def _calculate_cumulative_savings(self, years: int) -> float:
        """
        Calculate cumulative savings over years.

        Args:
            years: Number of years

        Returns:
            Total cumulative savings
        """
        total_savings = 0

        for year in range(1, years + 1):
            # Apply degradation and inflation
            year_savings = (
                self.annual_savings
                * ((1 - self.degradation_rate) ** (year - 1))
                * ((1 + self.inflation_rate) ** (year - 1))
            )
            total_savings += year_savings

        return total_savings

    def _generate_yearly_breakdown(self, years: int) -> List[Dict]:
        """
        Generate year-by-year breakdown.

        Args:
            years: Number of years to break down

        Returns:
            List of yearly data dictionaries
        """
        breakdown = []
        cumulative = 0

        for year in range(1, years + 1):
            # Calculate annual savings for this year
            year_savings = (
                self.annual_savings
                * ((1 - self.degradation_rate) ** (year - 1))
                * ((1 + self.inflation_rate) ** (year - 1))
            )
            cumulative += year_savings

            # Calculate ROI for this year
            roi = max(((cumulative - self.net_investment) / self.net_investment) * 100, 0)

            # Check if breakeven reached
            breakeven_reached = cumulative >= self.net_investment

            breakdown.append(
                {
                    "year": year,
                    "annual_savings": round(year_savings, 2),
                    "cumulative_savings": round(cumulative, 2),
                    "net_benefit": round(cumulative - self.net_investment, 2),
                    "roi_percentage": round(roi, 2),
                    "breakeven_reached": breakeven_reached,
                }
            )

        return breakdown
