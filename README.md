# CAPM Metrics

A stock performance tool based on the Capital Asset Pricing Model (CAPM). This package allows you to analyze stock performance and expected returns based on market data.

## Features

- Fetch historical stock data using the Yahoo Finance API.
- Calculate expected returns based on the CAPM model.
- Analyze stock performance against a market index.
- Get average yields from the 10-year Treasury note for risk-free return calculations.

## Installation

You can install the `capm-metrics` package via pip:

```bash
pip install capm-metrics
```

## Usage

Here's a basic example of how to use the `CAPMAnalyzer` class:

```python
from capm_metric import CAPMAnalyzer

# Create an instance of CAPMAnalyzer
analyzer = CAPMAnalyzer()

# Analyze a stock (e.g., Apple Inc. with ticker 'AAPL')
results = analyzer.analyze('AAPL', period='1y')

# Print the results
print(results)
```

### Parameters

- `symbol` (str): The stock symbol for analysis.
- `market` (str, optional): The market index symbol (default: `^GSPC`).
- `period` (str, optional): Valid periods for fetching data (e.g., `1d`, `1mo`, `1y`, etc.).
- `start` (str, optional): Download start date (YYYY-MM-DD).
- `end` (str, optional): Download end date (YYYY-MM-DD).

### Expected Output

The `analyze` method returns an `OrderedDict` containing:

- `company_name`: The full name of the company.
- `symbol`: The stock symbol.
- `start_date`: The start date of the analysis (YYYY-MM-DD).
- `end_date`: The end date of the analysis (YYYY-MM-DD).
- `expected_return`: The expected return calculated using CAPM.
- `actual_return`: The actual return calculated over the analysis period.
- `performance`: Indicates whether the stock overperformed or underperformed compared to the expected return.

## Example

```python
results = analyzer.analyze('AAPL', period='1y')
print(f"Expected Return: {results['expected_return']}")
print(f"Actual Return: {results['actual_return']}")
print(f"Performance: {results['performance']}")
```

## Dependencies

- `numpy`
- `pandas`
- `yfinance`

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request if you'd like to contribute.

## Acknowledgments

This package uses the `yfinance` library to fetch stock data, and the calculations are based on the Capital Asset Pricing Model (CAPM).
