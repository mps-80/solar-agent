# Sample Energy Usage Data for Solar ROI Analysis

This input file contains residential energy consumption data and financial parameters 
for calculating solar system ROI and breakeven analysis.

## Input Format

Create a JSON file with the following structure:

```json
{
  "property_id": "PROP001",
  "current_energy_usage_kwh": 12000,
  "estimated_annual_usage_kwh": 12500,
  "annual_usage_next_25_years": [12500, 12600, ...],
  "system_cost": 25000,
  "available_incentives": 5000,
  "location": "California",
  "system_efficiency": 0.95,
  "electricity_rate_per_kwh": 0.15
}
```

## Field Descriptions

- **property_id**: Unique identifier for the property
- **current_energy_usage_kwh**: Current annual energy usage in kWh
- **estimated_annual_usage_kwh**: Projection for next year's usage
- **annual_usage_next_25_years**: Array of 25 annual usage values (kWh)
- **system_cost**: Total cost of solar system installation
- **available_incentives**: Available federal tax credits, rebates, etc.
- **location**: Geographic location for policy relevant context
- **system_efficiency**: System efficiency rating (0.5 - 1.0), default 0.95
- **electricity_rate_per_kwh**: Current electricity rate per kWh, default $0.15

## Notes

- All monetary values in USD
- Energy usage values in kilowatt-hours (kWh)
- System efficiency accounts for inverter losses, shading, etc.
- The 25-year array is important for long-term ROI projections
