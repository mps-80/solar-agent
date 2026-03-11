"""
Breakeven analysis for solar investments
"""

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class BreakevenMetrics:
    """Breakeven analysis metrics"""
    breakeven_month: int
    breakeven_year: int
    months_to_breakeven: float
    cumulative_at_breakeven: float
    savings_per_month: float
    payback_period_years: float


class BreakevenAnalysis:
    """Analyze breakeven point for solar investments"""

    def __init__(
        self,
        net_investment: float,
        annual_savings: float,
        degradation_rate: float = 0.005,
        inflation_rate: float = 0.03,
    ):
        """
        Initialize breakeven analysis.

        Args:
            net_investment: Net cost after incentives
            annual_savings: Annual energy savings
            degradation_rate: Annual panel degradation
            inflation_rate: Annual inflation rate
        """
        self.net_investment = net_investment
        self.annual_savings = annual_savings
        self.degradation_rate = degradation_rate
        self.inflation_rate = inflation_rate

    def analyze(self) -> BreakevenMetrics:
        """
        Perform breakeven analysis.

        Returns:
            BreakevenMetrics object
        """
        # Calculate month-by-month
        cumulative = 0
        months = 0
        monthly_rate = 1 - (self.degradation_rate / 12)

        while cumulative < self.net_investment and months < 600:
            month = months + 1
            year = (month - 1) // 12
            month_in_year = (month - 1) % 12 + 1

            # Monthly savings with degradation and inflation
            monthly_savings = (
                (self.annual_savings / 12)
                * ((1 - self.degradation_rate) ** year)
                * ((1 + self.inflation_rate) ** year)
            )

            cumulative += monthly_savings
            months = month

        breakeven_month = months
        breakeven_year = months // 12
        months_remainder = months % 12
        avg_monthly_savings = self.net_investment / (breakeven_month or 1)

        return BreakevenMetrics(
            breakeven_month=breakeven_month,
            breakeven_year=breakeven_year,
            months_to_breakeven=breakeven_month,
            cumulative_at_breakeven=cumulative,
            savings_per_month=avg_monthly_savings,
            payback_period_years=breakeven_month / 12,
        )

    def generate_breakeven_report(self, yearly_data: List[Dict]) -> Dict:
        """
        Generate detailed breakeven report.

        Args:
            yearly_data: Yearly breakdown from ROICalculator

        Returns:
            Detailed breakeven report
        """
        breakeven = self.analyze()

        # Find first positive year
        positive_year = None
        for year_data in yearly_data:
            if year_data["breakeven_reached"]:
                positive_year = year_data["year"]
                break

        report = {
            "summary": {
                "payback_period_months": breakeven.breakeven_month,
                "payback_period_years": round(breakeven.payback_period_years, 2),
                "breakeven_month": breakeven.breakeven_month % 12 or 12,
                "breakeven_year": breakeven.breakeven_year + (1 if breakeven.breakeven_month % 12 else 0),
                "average_monthly_savings": round(breakeven.savings_per_month, 2),
            },
            "timeline": {
                "investment_required": self.net_investment,
                "cumulative_at_breakeven": round(breakeven.cumulative_at_breakeven, 2),
                "months_to_roi_positive": breakeven.breakeven_month,
                "year_roi_positive": positive_year,
            },
            "analysis": {
                "degradation_impact": f"{self.degradation_rate * 100}% annually",
                "inflation_considered": f"{self.inflation_rate * 100}% annually",
                "calculation_period": "25 years",
            },
        }

        return report
