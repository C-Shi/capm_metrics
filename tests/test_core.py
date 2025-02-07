# pylint: disable=W0212
"""Test Core Module"""
from unittest import TestCase
from unittest.mock import patch, MagicMock, call, ANY
from collections import OrderedDict
import pandas as pd
from capm_metric.capm import CAPMAnalyzer

class TestCAPMAnalyzer(TestCase):
    """Test Class for CAPMAnalyzer class in capm module"""
    @patch("capm_metric.capm.yf.Ticker")
    def test_get_avg_treasury_10y_yield(self, mock_ticker):
        """Test protected method _get_avg_treasury_10y_yield"""
        analyzer = CAPMAnalyzer()
        mock_ticker.return_value.history.return_value = pd.DataFrame({
            "Close": [1.5, 1.6, 1.7, 1.8]
        })
        yield_result = analyzer._get_avg_treasury_10y_yield()

        mock_ticker.assert_called_with("^TNX")
        self.assertEqual(yield_result, 1.65)

    @patch("capm_metric.capm.yf.Ticker")
    def test_fetch_stock_data(self, mock_ticker):
        """Test protected method fetch_stock_data"""
        analyzer = CAPMAnalyzer()

        # scenario 1 => if no close data raise value error
        mock_ticker.return_value.history.return_value = pd.DataFrame(columns=['Close'])
        with self.assertRaises(ValueError):
            analyzer.fetch_stock_data("AAPL")

        mock_ticker.return_value.history.return_value = pd.DataFrame({
            "Close": [1.0, 2.0, 3.0, 4.0, 5.0]
        })
        # scenario 2 => rename columns and return for market
        _, mock_market = analyzer.fetch_stock_data(ANY, is_market=True, period="5d")
        pd.testing.assert_frame_equal(mock_market, pd.DataFrame({
            "market": [1.0, 2.0, 3.0, 4.0, 5.0]

        }, index=pd.RangeIndex(start=0, stop=5, name='Date')))

        # scenario 3 => rename columns and return for stock
        mock_info, mock_df = analyzer.fetch_stock_data("AAPL", period="5d")

        self.assertEqual(mock_info, mock_ticker.return_value.info)
        pd.testing.assert_frame_equal(mock_df, pd.DataFrame({
            "AAPL": [1.0, 2.0, 3.0, 4.0, 5.0]

        }, index=pd.RangeIndex(start=0, stop=5, name='Date')))

    def test_actual_return(self):
        """Test protected method _actual_return"""
        analyzer = CAPMAnalyzer()

        with self.assertRaises(ValueError) as context:
            analyzer._actual_return(100, 0)
        self.assertEqual(str(context.exception), "Start price cannot be zero")

        self.assertEqual(analyzer._actual_return(100, 50), 1.0)

    @patch("capm_metric.capm.yf.Ticker")
    def test_analyze(self, _):
        """Test capm, public method analyze"""
        analyzer = CAPMAnalyzer()

        # Scenario 1 => missing argument
        with self.assertRaises(ValueError) as context:
            analyzer.analyze("AAPL")
        self.assertEqual(
            str(context.exception),
            "Either 'period' or both 'start' and 'end' must be specified."
        )

        # Scenario 2 => fetch data
        TEST_SYMBOL = "AAPL" # pylint: disable=invalid-name
        stock_data_mock = (MagicMock(), pd.DataFrame({
            TEST_SYMBOL: [100, 200, 300, 400, 500]
        }, index=pd.date_range(start="2024-12-16", end="2024-12-20", name="Date")))
        market_data_mock = (MagicMock(), pd.DataFrame({
            "market": [1000, 2000, 3000, 4000, 5000]
        }, index=pd.date_range(start="2024-12-16", end="2024-12-20", name="Date")))
        with patch(
            "capm_metric.capm.CAPMAnalyzer.fetch_stock_data",
            side_effect=[stock_data_mock, market_data_mock]
        ) as fetch_stock_data_mock, patch(
            "capm_metric.capm.CAPMAnalyzer._get_avg_treasury_10y_yield",
            return_value=0.4
        ) as treasury_yield_mock:
            result = analyzer.analyze(TEST_SYMBOL, period="1y")

            fetch_stock_data_mock.assert_has_calls([
                call(TEST_SYMBOL, period="1y"),
                call("^GSPC", is_market=True, period="1y")
            ])

            treasury_yield_mock.assert_called_with(period="1y")

            self.assertIsInstance(result, OrderedDict)

            self.assertEqual(list(result.keys()), [
                "company_name", "symbol", "start_date", "end_date",
                "expected_return", "actual_return",
                "performance"
            ])
    @patch("capm_metric.capm.yf.Ticker")
    def test_analyze_local(self, _):
        data = {
            "Date": pd.to_datetime([
                "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05", "2023-01-06"
            ]),
            "Daily Return": [0.0012, -0.0008, 0.0025, -0.0012, 0.0007],  # Sample stock daily returns
            "Daily Return Market": [0.0009, -0.0005, 0.0020, -0.0007, 0.0004]  # Sample market daily returns
        }

        stock_df = pd.DataFrame(data)

        analyzer = CAPMAnalyzer()

        result = analyzer.analyze_local(stock_df, 0.1)

        self.assertIsInstance(result, OrderedDict)
        self.assertEqual(list(result.keys()), [
            "expected_return",
            "actual_return",
            "performance"
        ])
