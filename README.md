# Solar ROI Calculator with RAG Policy Analysis

A Python application for calculating solar system ROI (Return on Investment) and breakeven analysis using RAG (Retrieval-Augmented Generation) for intelligent policy interpretation.

## Features

- **RAG-Based Policy Analysis**: Uses LangChain with Groq LLM to search and understand solar policies
- **ROI Calculation**: Computes breakeven point based on energy usage and 25-year projections
- **JSON Input Processing**: Accepts energy usage data in JSON format
- **Policy Management**: Reads solar policies from local files for context-aware analysis

## Project Structure

```
photon-ai/
├── src/
│   ├── rag/                 # RAG pipeline and policy retrieval
│   ├── roi/                 # ROI calculation logic
│   ├── utils/               # Configuration and utilities
│   └── __init__.py
├── data/
│   ├── policies/            # Solar policy documents
│   ├── inputs/              # Input JSON files with energy data
│   └── outputs/             # Generated ROI analysis results
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
└── README.md
```

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your Groq API key:
```
GROQ_API_KEY=your_api_key_here
```

## Usage

### Prepare Input Data
Create a JSON file in `data/inputs/` with energy usage data:

```json
{
  "property_id": "PROP001",
  "current_energy_usage_kwh": 12000,
  "estimated_annual_usage_kwh": 12500,
  "annual_usage_next_25_years": [12500, 12600, 12700, ...],
  "system_cost": 25000,
  "available_incentives": 5000,
  "location": "California"
}
```

### Add Policy Documents
Place solar policy documents in `data/policies/` folder.

### Run Analysis
```bash
python main.py --input data/inputs/energy_data.json --output data/outputs/roi_analysis.json
```

## Configuration

Edit `src/utils/config.py` to customize:
- LLM model selection (Groq model)
- RAG vector store settings
- ROI calculation parameters
- Breakeven analysis thresholds

## Output

The application generates a JSON report containing:
- Breakeven period (months/years)
- ROI percentage
- 25-year projection with cumulative savings
- Policy insights and applicable incentives

## Dependencies

- **LangChain**: LLM framework
- **Groq**: Fast LLM inference
- **FAISS**: Vector similarity search
- **sentence-transformers**: Embeddings generation
- **PyPDF2**: PDF processing for policies

