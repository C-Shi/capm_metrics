"""Core Module"""
import warnings
from collections import OrderedDict
from typing import Tuple, Dict
import yfinance as yf
import pandas as pd
import numpy as np

TRADING_DAYS_PER_YEAR = 252

class CAPMAnalyzer:
    """Class for analyzing stock performance based on CAPM model"""
    def __init__(self):
        self._ticker = yf.Ticker

    def _get_avg_treasury_10y_yield(self, **kwargs) -> float:
        """
        Fetches the historical data for the 10-year Treasury note
        and calculates its average yield.

        :kwargs:
            period: str, optional
                The period for which to fetch historical data. 
                Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max.

        :return: 
            float: The average yield of the 10-year Treasury note.
        """

        treasury_10y = self._ticker("^TNX")
        treasury_10y_his = treasury_10y.history(**kwargs)
        avg_yield = treasury_10y_his['Close'].mean()
        return float(avg_yield)

    def fetch_stock_data(
        self,
        symbol: str,
        is_market: bool = False,
        **kwargs
    ) -> Tuple[Dict[str, str], pd.DataFrame]:
        """
        Fetches historical stock data for a given symbol.

        :param symbol: str
            The stock symbol to fetch data for.
        
        :param is_market: bool, optional
            A flag indicating whether the data is for a market index.
            Default is False.
        
        :param period: str, optional
            The period for which to fetch historical data. 
            Balid values: '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'.
            If specified, this will override the `start` and `end` for defining the range.
            Note: `period` and `start`/`end` should not be used together. Choose one or the other.
    
        :param start: str or datetime, optional
            The start date string in the format 'YYYY-MM-DD' or a datetime object. 
            Used to specify the start date for the data range.
            If `period` is not provided, `start` and `end` must be supplied together.

        :param end: str or datetime, optional
            The end date string in the format 'YYYY-MM-DD' or a datetime object. 
            Used to specify the end date for the data range.
            If `period` is provided, this parameter will be ignored.
            If `start` is specified, `end` must also be supplied to define the range.

        :return: 
            Tuple[Dict[str, str], pd.DataFrame]: A tuple containing 
            the stock information as a dictionary and the historical 
            price data as a DataFrame.
        """
        stock = self._ticker(symbol)

        df = stock.history(**kwargs)[['Close']]

        if df.empty:
            raise ValueError(
                f"No data found for symbol {symbol}. "
                f"Possible wrong symbol or no data available for the specified period.")

        if is_market:
            df.rename(columns={'Close': "market"}, inplace=True)
        else:
            df.rename(columns={'Close': symbol}, inplace=True)
        df.index.name = "Date"

        return stock.info, df

    def _actual_return(self, end: np.float64, start: np.float64) -> np.float64:
        """
        Calculates the actual return of an investment.

        :param end: float
            The ending price of the investment.
        
        :param start: float
            The starting price of the investment.

        :return: 
            float: The actual return as a decimal.
        
        :raises ValueError: If start price is zero.
        """
        if start == 0:
            raise ValueError("Start price cannot be zero")
        return (end - start) / start

    def analyze(self, symbol: str, market: str = "^GSPC", **kwargs) -> OrderedDict:
        """
        Analyzes the stock and calculates CAPM metrics.

        :param symbol: str
            The stock symbol for analysis.

        :param market: str, optional
            The market index symbol (default: ^GSPC).

        :param period: str, optional
            The period for which to fetch historical data. 
            Valid values: '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'.
            If specified, this will override the `start` and `end` for defining the range.
            Note: `period` and `start`/`end` should not be used together. Choose one or the other.
    
        :param start: str or datetime, optional
            The start date string in the format 'YYYY-MM-DD' or a datetime object. 
            Used to specify the start date for the data range.
            If `period` is not provided, `start` and `end` must be supplied together.

        :param end: str or datetime, optional
            The end date string in the format 'YYYY-MM-DD' or a datetime object. 
            Used to specify the end date for the data range.
            If `period` is provided, this parameter will be ignored.
            If `start` is specified, `end` must also be supplied to define the range.

        :return: 
            OrderedDict: A dictionary containing the following keys:
            - company_name: The full name of the company.
            - symbol: The stock symbol.
            - start_date: The start date of the analysis (YYYY-MM-DD).
            - end_date: The end date of the analysis (YYYY-MM-DD).
            - expected_return: The expected return calculated using CAPM.
            - actual_return: The actual return calculated over the analysis period.
            - performance: A string indicating whether the stock 
              overperformed or underperformed compared to the expected return.
        
        :raises ValueError: If neither 'period' nor both 'start' and 'end' are specified.
        """
        if 'period' not in kwargs and not ('start' in kwargs and 'end' in kwargs):
            raise ValueError("Either 'period' or both 'start' and 'end' must be specified.")

        # get stock data
        symbol_info, symbol_df = self.fetch_stock_data(symbol, **kwargs)

        data_duration = symbol_df.index[-1] - symbol_df.index[0]
        if data_duration.days < 365:
            warnings.warn(
                "Warning: Period less than 1 year may not provide accurate result",
                stacklevel=2
            )

        # get market data
        _, market_df = self.fetch_stock_data(market, is_market=True, **kwargs)

        stock_df = pd.merge(symbol_df, market_df, how="inner", on="Date")
        # Calculate daily return and market daily return
        stock_df["Daily Return"] = stock_df[symbol].pct_change()
        stock_df["Daily Return Market"] = stock_df["market"].pct_change()
        stock_df.fillna(0, inplace=True)

        # calculate market free return using US 10 year treasury note
        rf = self._get_avg_treasury_10y_yield(**kwargs)

        # calculate alpha, beta using linear regression
        beta, _ = np.polyfit(
            stock_df["Daily Return Market"],
            stock_df["Daily Return"],
            deg=1
        )

        # calculate annualized market return
        average_daily_return = stock_df["Daily Return Market"].mean()
        rm = average_daily_return * TRADING_DAYS_PER_YEAR

        # R_exp = R_risk_free + beta * (R_market - R_risk_free)
        # Calculate expected return
        r_exp = rf + beta * (rm - rf)

        r_act = self._actual_return(stock_df[symbol].iloc[-1], stock_df[symbol].iloc[0])

        return OrderedDict({
            "company_name": symbol_info['longName'],
            "symbol": symbol,
            "start_date": stock_df.index[0].strftime('%Y-%m-%d'),
            "end_date": stock_df.index[-1].strftime('%Y-%m-%d'),
            "expected_return": float(r_exp),
            "actual_return": float(r_act),
            "performance": "overperform" if r_act - r_exp > 0 else "underperform"
        })

    def analyze_local(self, stock_df: pd.DataFrame, r_act: float, risk_free_rate: float = 0.0):
        """
        Analyze stock performance based on daily returns.

        :param stock_df: pd.DataFrame
            A DataFrame containing at least:
            - "Daily Return" (Stock's daily return)
            - "Daily Return Market" (Market's daily return)
        
        :param r_act: float
            The actual return of the stock (should be annualized).
        
        :param risk_free_rate: float, optional
            The annualized risk-free rate, default is 0.0.
        
        :return: OrderedDict
            - expected_return: Expected return based on CAPM.
            - actual_return: The actual return provided.
            - performance: Overperform or underperform relative to expected return.
        """

        stock_df = stock_df.sort_values("Date")
        required_columns = [ "Date", "Daily Return", "Daily Return Market" ]

        for c in required_columns:
            if c not in stock_df.columns:
                raise ValueError(f"Column {c} is missing")

        if stock_df["Daily Return Market"].std() == 0:
            raise ValueError("Market Return has zero variance")

        beta, _ = np.polyfit(
            stock_df["Daily Return Market"],
            stock_df["Daily Return"],
            deg=1
        )

        rm = stock_df["Daily Return Market"].mean() * TRADING_DAYS_PER_YEAR

        r_exp = risk_free_rate + beta * (rm - risk_free_rate)

        return OrderedDict({
            "expected_return": float(r_exp),
            "actual_return": float(r_act),
            "performance": "overperform" if r_act - r_exp > 0 else "underperform"
        })
