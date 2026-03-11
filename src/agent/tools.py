"""
Agent tools for Solar ROI Analysis
"""

from typing import Dict, Any
from langchain_core.tools import tool
from src.utils.io_utils import InputProcessor
from src.rag.policy_loader import PolicyLoader
from src.rag.retriever import PolicyRetriever
from src.roi.calculator import ROICalculator
from src.roi.breakeven import BreakevenAnalysis
from src.utils.config import Config
from src.utils.logger import get_logger

logger = get_logger(__name__)


@tool
def load_energy_data(input_file: str) -> Dict[str, Any]:
    """
    Load and validate energy usage data from JSON file.
    
    Args:
        input_file: Path to JSON file with energy data
        
    Returns:
        Dictionary with property info and energy data
    """
    try:
        energy_data = InputProcessor.load_input(input_file)
        return {
            "success": True,
            "property_id": energy_data.property_id,
            "location": energy_data.location,
            "annual_usage_kwh": energy_data.estimated_annual_usage_kwh,
            "system_cost": energy_data.system_cost,
            "available_incentives": energy_data.available_incentives,
            "system_efficiency": energy_data.system_efficiency,
            "electricity_rate_per_kwh": energy_data.electricity_rate_per_kwh,
            "annual_usage_25_years": len(energy_data.annual_usage_next_25_years)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@tool
def search_location_policies(location: str) -> Dict[str, Any]:
    """
    Search and load solar policy documents for a specific location.
    Loads both location-specific and general policies.
    
    Args:
        location: Location name (e.g., "Karnataka", "California")
        
    Returns:
        Dictionary with loaded policies and documents count
    """
    try:
        policy_loader = PolicyLoader(Config.POLICY_DIR)
        documents = policy_loader.load_policies(location=location)
        
        if not documents:
            return {
                "success": False,
                "message": f"No policies found for {location}",
                "policies_loaded": 0
            }
        
        return {
            "success": True,
            "location": location,
            "policies_loaded": len(documents),
            "policy_files": [
                doc.metadata.get("filename", "Unknown") 
                for doc in documents
            ]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@tool
def analyze_policy_incentives(location: str, policies_data: str) -> Dict[str, Any]:
    """
    Analyze available tax credits and incentives for a location using RAG.
    
    Args:
        location: Property location
        policies_data: Information about loaded policies
        
    Returns:
        Dictionary with policy insights and incentives
    """
    try:
        logger.info(f"[analyze_policy_incentives] Starting RAG analysis for {location}")
        policy_loader = PolicyLoader(Config.POLICY_DIR)
        documents = policy_loader.load_policies(location=location)
        
        logger.info(f"[analyze_policy_incentives] Loaded {len(documents) if documents else 0} documents")
        
        if not documents:
            return {
                "success": False,
                "insights": "No policies available for analysis"
            }
        
        logger.info(f"[analyze_policy_incentives] Creating retriever...")
        retriever = PolicyRetriever(documents)
        query = f"What are the available solar tax credits, rebates, and incentives for {location}? What are the eligibility requirements?"
        
        logger.info(f"[analyze_policy_incentives] Invoking RAG chain with query...")
        result = retriever.answer_question(query)
        logger.info(f"[analyze_policy_incentives] RAG query complete")
        
        return {
            "success": True,
            "location": location,
            "query": query,
            "incentives_found": result["answer"],
            "sources": len(result["sources"])
        }
    except Exception as e:
        logger.error(f"[analyze_policy_incentives] Error - {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


@tool
def calculate_roi_metrics(
    system_cost: float,
    available_incentives: float,
    annual_usage_kwh: float,
    system_efficiency: float,
    electricity_rate: float
) -> Dict[str, Any]:
    """
    Calculate ROI metrics including breakeven period and financial projections.
    
    Args:
        system_cost: Total solar system installation cost
        available_incentives: Available tax credits and rebates
        annual_usage_kwh: Annual energy usage in kWh
        system_efficiency: System efficiency rating (0-1)
        electricity_rate: Current electricity rate per kWh
        
    Returns:
        Dictionary with ROI calculations
    """
    try:
        # Calculate annual savings
        annual_savings = annual_usage_kwh * system_efficiency * electricity_rate
        
        # Initialize calculator
        roi_calc = ROICalculator(
            system_cost=system_cost,
            available_incentives=available_incentives,
            annual_savings=annual_savings,
            degradation_rate=Config.DEFAULT_DEGRADATION_RATE,
            inflation_rate=Config.DEFAULT_INFLATION_RATE
        )
        
        roi_result = roi_calc.calculate_roi()
        
        return {
            "success": True,
            "system_cost": system_cost,
            "net_investment": roi_result.net_investment,
            "annual_savings": roi_result.annual_savings,
            "breakeven_years": round(roi_result.breakeven_years, 2),
            "breakeven_months": round(roi_result.breakeven_months, 1),
            "roi_5_years": round(roi_result.roi_percentage_5yr, 2),
            "roi_10_years": round(roi_result.roi_percentage_10yr, 2),
            "roi_25_years": round(roi_result.roi_percentage_25yr, 2),
            "cumulative_savings_25yr": round(roi_result.cumulative_savings_25yr, 2)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@tool
def perform_breakeven_analysis(
    net_investment: float,
    annual_savings: float
) -> Dict[str, Any]:
    """
    Perform detailed breakeven analysis with month-by-month projections.
    
    Args:
        net_investment: Net cost after incentives
        annual_savings: Estimated annual savings
        
    Returns:
        Dictionary with breakeven metrics and timeline
    """
    try:
        breakeven = BreakevenAnalysis(
            net_investment=net_investment,
            annual_savings=annual_savings,
            degradation_rate=Config.DEFAULT_DEGRADATION_RATE,
            inflation_rate=Config.DEFAULT_INFLATION_RATE
        )
        
        metrics = breakeven.analyze()
        
        return {
            "success": True,
            "payback_period_months": metrics.breakeven_month,
            "payback_period_years": round(metrics.payback_period_years, 2),
            "monthly_savings": round(metrics.savings_per_month, 2),
            "cumulative_at_breakeven": round(metrics.cumulative_at_breakeven, 2),
            "degradation_rate": "0.5%",
            "inflation_rate": "3.0%"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@tool
def generate_roi_recommendation(
    breakeven_years: float,
    roi_25_years: float,
    net_investment: float
) -> Dict[str, Any]:
    """
    Generate recommendation based on ROI analysis.
    
    Args:
        breakeven_years: Years to break even
        roi_25_years: ROI percentage over 25 years
        net_investment: Net investment required
        
    Returns:
        Dictionary with recommendation and analysis
    """
    try:
        recommendation = "RECOMMENDED"
        confidence = 0
        reason = []
        
        # Analyze breakeven
        if breakeven_years <= 8:
            reason.append(f"Fast breakeven in {breakeven_years} years")
            confidence += 40
        elif breakeven_years <= 12:
            reason.append(f"Moderate breakeven in {breakeven_years} years")
            confidence += 20
        else:
            reason.append(f"Longer breakeven period of {breakeven_years} years")
            recommendation = "NOT_RECOMMENDED"
        
        # Analyze long-term ROI
        if roi_25_years > 200:
            reason.append(f"Excellent 25-year ROI of {roi_25_years}%")
            confidence += 40
        elif roi_25_years > 100:
            reason.append(f"Good 25-year ROI of {roi_25_years}%")
            confidence += 20
        else:
            reason.append(f"Moderate 25-year ROI of {roi_25_years}%")
        
        # Analyze investment
        if net_investment < 30000:
            reason.append("Reasonable investment amount")
            confidence += 20
        
        return {
            "success": True,
            "recommendation": recommendation,
            "confidence_score": min(confidence, 100),
            "reasons": reason,
            "summary": f"Investment of Rs. {net_investment:,.0f} with breakeven in {breakeven_years} years"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
