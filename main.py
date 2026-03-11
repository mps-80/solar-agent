"""
Main application - Solar ROI Calculator with RAG Policy Analysis using Agent
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any

from src.utils.logger import get_logger
from src.utils.config import Config
from src.utils.io_utils import OutputFormatter
from src.agent.orchestrator import SolarROIAgent

logger = get_logger(__name__)


class SolarROIAnalyzer:
    """Main application orchestrator using LangChain Agent"""

    def __init__(self):
        """Initialize the analyzer with agent"""
        self.agent = SolarROIAgent()

    def run(self, input_file: str, output_file: str = None) -> str:
        """
        Run complete analysis pipeline using agent.

        Args:
            input_file: Path to input JSON file
            output_file: Optional output filename

        Returns:
            Path to output file
        """
        try:
            logger.info("=" * 60)
            logger.info("Solar ROI Calculator with RAG Policy Analysis (Agent-Based)")
            logger.info("=" * 60)

            # Run agent analysis
            analysis_result = self.agent.analyze(input_file)

            if not analysis_result.get("success", False):
                logger.error(f"Agent analysis failed: {analysis_result.get('error', 'Unknown error')}")
                raise Exception(analysis_result.get("error", "Agent analysis failed"))

            # Save results
            output_path = OutputFormatter.save_results(
                analysis_result, filename=output_file
            )
            logger.info(f"Results saved to: {output_path}")

            return output_path

        except Exception as e:
            logger.error(f"Application error: {str(e)}")
            raise



def main():
    """Application entry point"""
    parser = argparse.ArgumentParser(
        description="Solar ROI Calculator with RAG Policy Analysis"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input JSON file with energy usage data",
    )
    parser.add_argument(
        "--output",
        help="Output filename (optional)",
    )
    parser.add_argument(
        "--api-key",
        help="Groq API key (or set GROQ_API_KEY environment variable)",
    )

    args = parser.parse_args()

    # Set API key if provided
    if args.api_key:
        Config.GROQ_API_KEY = args.api_key

    # Validate API key
    if not Config.GROQ_API_KEY:
        logger.error("GROQ_API_KEY not set. Set it as environment variable or pass --api-key")
        sys.exit(1)

    # Run analyzer
    analyzer = SolarROIAnalyzer()
    output_path = analyzer.run(args.input, args.output)

    print(f"\n✓ Analysis complete. Results saved to: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
