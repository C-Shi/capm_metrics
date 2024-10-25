from collections import OrderedDict
from typing import Tuple, Dict
import yfinance as yf
import pandas as pd
import numpy as np

TRADING_DAYS_PER_YEAR = 252

class CAPMAnalyzer:
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
    
    def _fetch_stock_data(self, symbol: str, is_market: bool = False, **kwargs) -> Tuple[Dict[str, str], pd.DataFrame]:
        """
        Fetches historical stock data for a given symbol.

        :param symbol: str
            The stock symbol to fetch data for.
        
        :param is_market: bool, optional
            A flag indicating whether the data is for a market index.
            Default is False.
        
        :kwargs:
            period: str, optional
                The period for which to fetch historical data. 
                Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max.
            start: str, optional
                Download start date string (YYYY-MM-DD) or datetime.
            end: str, optional
                Download end date string (YYYY-MM-DD) or datetime.

        :return: 
            Tuple[Dict[str, str], pd.DataFrame]: A tuple containing 
            the stock information as a dictionary and the historical 
            price data as a DataFrame.
        """
        stock = self._ticker(symbol)

        df = stock.history(**kwargs)[['Close']]

        if df.empty:
            raise ValueError(f"No data found for symbol {symbol}. Possible wrong symbol or no data available for the specified period.")

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

        :kwargs:
            period: str, optional
                Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max.
            start: str, optional
                Download start date string (YYYY-MM-DD) or datetime, inclusive.
            end: str, optional
                Download end date string (YYYY-MM-DD) or datetime, exclusive.

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
        symbol_info, symbol_df = self._fetch_stock_data(symbol, **kwargs)

        # get market data
        _, market_df = self._fetch_stock_data(market, is_market=True, **kwargs)

        stock_df = pd.merge(symbol_df, market_df, how="inner", on="Date")
        # Calculate daily return and market daily return
        stock_df["Daily Return"] = stock_df[symbol].pct_change()
        stock_df["Daily Return Market"] = stock_df["market"].pct_change()
        stock_df.fillna(0, inplace=True)

        # calculate alpha, beta using linear regression
        beta, _ = np.polyfit(
            stock_df["Daily Return Market"],
            stock_df["Daily Return"],
            deg=1
        )

        # calculate market free return using US 10 year treasury note
        rf = self._get_avg_treasury_10y_yield(**kwargs)

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