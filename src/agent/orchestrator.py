"""
Agent orchestrator for Solar ROI Analysis
"""

from typing import Dict, Any, List
import json
from langchain_groq import ChatGroq
from src.agent.tools import (
    load_energy_data,
    search_location_policies,
    analyze_policy_incentives,
    calculate_roi_metrics,
    perform_breakeven_analysis,
    generate_roi_recommendation
)
from src.utils.config import Config
from src.utils.logger import get_logger
from src.utils.io_utils import OutputFormatter

logger = get_logger(__name__)


class SolarROIAgent:
    """Agent for autonomous solar ROI analysis"""

    def __init__(self):
        """Initialize the agent with tools"""
        self.llm = ChatGroq(
            model=Config.GROQ_MODEL,
            temperature=0.3,
            api_key=Config.GROQ_API_KEY
        )
        
        self.tools_map = {
            "load_energy_data": load_energy_data,
            "search_location_policies": search_location_policies,
            "analyze_policy_incentives": analyze_policy_incentives,
            "calculate_roi_metrics": calculate_roi_metrics,
            "perform_breakeven_analysis": perform_breakeven_analysis,
            "generate_roi_recommendation": generate_roi_recommendation,
        }

    def analyze(self, input_file: str) -> Dict[str, Any]:
        """
        Run the agent to analyze solar ROI.
        
        Args:
            input_file: Path to input JSON file
            
        Returns:
            Complete analysis results
        """
        try:
            logger.info("=" * 60)
            logger.info("Solar ROI Agent Analysis Starting")
            logger.info("=" * 60)
            
            logger.info(f"Starting agent analysis for: {input_file}")
            
            # Execute analysis tools sequentially
            analysis_results = self._execute_sequential_analysis(input_file)
            
            logger.info("Agent analysis completed successfully")
            
            return {
                "success": True,
                "analysis_results": analysis_results,
                "timestamp": self._get_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Agent analysis error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _execute_sequential_analysis(self, input_file: str) -> Dict[str, Any]:
        """Execute analysis tools sequentially"""
        results = {}
        
        try:
            # 1. Load energy data
            logger.info("Step 1: Loading energy data...")
            load_result = load_energy_data.invoke({"input_file": input_file})
            results["load_energy_data"] = load_result
            logger.info(f"Energy data loaded: {load_result.get('success')}")
            
            if not load_result.get("success", False):
                logger.error(f"Failed to load energy data: {load_result.get('error')}")
                return results
            
            energy_data = load_result
            location = energy_data.get("location", "Unknown")
            logger.info(f"Location: {location}")
            
            # 2. Search policies
            logger.info("Step 2: Searching location policies...")
            policy_result = search_location_policies.invoke(
                {"location": location}
            )
            results["search_location_policies"] = policy_result
            logger.info(f"Policies loaded: {policy_result.get('success')}")
            
            # 3. Analyze incentives
            logger.info("Step 3: Analyzing incentives...")
            incentive_result = analyze_policy_incentives.invoke(
                {"location": location, "policies_data": str(policy_result)}
            )
            results["analyze_policy_incentives"] = incentive_result
            logger.info(f"Incentive analysis complete: {incentive_result.get('success')}")
            
            # 4. Calculate ROI
            logger.info("Step 4: Calculating ROI metrics...")
            roi_result = calculate_roi_metrics.invoke({
                "system_cost": float(energy_data.get("system_cost", 0)),
                "available_incentives": float(energy_data.get("available_incentives", 0)),
                "annual_usage_kwh": float(energy_data.get("annual_usage_kwh", 0)),
                "system_efficiency": float(energy_data.get("system_efficiency", 0.95)),
                "electricity_rate": float(energy_data.get("electricity_rate_per_kwh", 0.15))
            })
            results["calculate_roi_metrics"] = roi_result
            logger.info(f"ROI calculation complete: {roi_result.get('success')}")
            
            if not roi_result.get("success", False):
                logger.error(f"Failed to calculate ROI: {roi_result.get('error')}")
                return results
            
            roi_data = roi_result
            
            # 5. Breakeven analysis
            logger.info("Step 5: Performing breakeven analysis...")
            breakeven_result = perform_breakeven_analysis.invoke({
                "net_investment": float(roi_data.get("net_investment", 0)),
                "annual_savings": float(roi_data.get("annual_savings", 0))
            })
            results["perform_breakeven_analysis"] = breakeven_result
            logger.info(f"Breakeven analysis complete: {breakeven_result.get('success')}")
            
            # 6. Generate recommendation
            logger.info("Step 6: Generating recommendation...")
            recommendation_result = generate_roi_recommendation.invoke({
                "breakeven_years": float(roi_data.get("breakeven_years", 0)),
                "roi_25_years": float(roi_data.get("roi_25_years", 0)),
                "net_investment": float(roi_data.get("net_investment", 0))
            })
            results["generate_roi_recommendation"] = recommendation_result
            logger.info(f"Recommendation generated: {recommendation_result.get('success')}")
            
        except Exception as e:
            logger.error(f"Sequential analysis error: {str(e)}", exc_info=True)
            results["error"] = str(e)
        
        return results

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
