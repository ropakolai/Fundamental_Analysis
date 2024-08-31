import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import numpy as np 
import numpy_financial as npf
import datetime


def fetch_financial_data(ticker, growth_assumption):
    # Fetch stock data using yfinance
    stock = yf.Ticker(ticker)
    
    # Income Statement
    income_statement = stock.financials.T
    cash_flow_statement = stock.cashflow.T
    balance_sheet = stock.balance_sheet.T
    

    # Extract necessary fields
    financial_data = {}

    # Constants
    risk_free_rate = 0.0459
    market_return = 0.085
    growth_rate = 0.01
    perpetual_growth_rate = 0.02
    growth_multiple = 8.3459 * (1.07) ** (growth_assumption - 4)

   # Calculate Total Debt
    financial_data['Total Debt']= balance_sheet['Total Debt'].iloc[0]

    # Cash and Cash Equivalents
    financial_data['Cash and Cash Equivalents'] = balance_sheet['Cash And Cash Equivalents'].iloc[0]

    # Invested Capital for 2023 and 2022
    financial_data['Invested Capital 2023'] = balance_sheet['Total Assets'].iloc[0] - balance_sheet['Total Liabilities Net Minority Interest'].iloc[0]
    financial_data['Invested Capital 2022'] = balance_sheet['Total Assets'].iloc[1] - balance_sheet['Total Liabilities Net Minority Interest'].iloc[1]

    # Interest Expense
    try:
        financial_data['Interest Expense'] = income_statement['Interest Expense'].iloc[0]
    except (KeyError, IndexError):
        financial_data['Interest Expense'] = 0


    # Income Tax Expense
    financial_data['Tax Provision'] = income_statement['Tax Provision'].iloc[0]

    # Income Before Tax
    financial_data['Pretax Income'] = income_statement['Pretax Income'].iloc[0]

     # Total Revenue
    financial_data['Total Revenue'] = income_statement['Total Revenue'].iloc[0]

    # Operating Income
    financial_data['Operating Income'] = income_statement['Operating Income'].iloc[0]

    # Calculate Weight of Debt
    financial_data['Effective Tax Rate'] = financial_data['Tax Provision'] / financial_data['Pretax Income']
    financial_data['Cost of Debt'] = financial_data['Interest Expense'] / financial_data['Total Debt']

    # Market Cap
    financial_data['Market Cap'] = stock.info['marketCap']

    # Beta
    financial_data['Beta'] = stock.info.get('beta', 'Not Found')

    # Outstanding Shares
    financial_data['Outstanding Shares'] = stock.info['sharesOutstanding']

    # Operating Cash Flow
    financial_data['Operating Cash Flow'] = cash_flow_statement['Operating Cash Flow'].iloc[0]

    # Capital Expenditure
    financial_data['Capital Expenditure'] = cash_flow_statement['Capital Expenditure'].iloc[0]

    # Calculate Debt Minus Market Cap
    financial_data['Debt plus Market Cap'] = financial_data['Total Debt'] + financial_data['Market Cap']

    # Calculate Weight of Debt
    financial_data['Weight of Debt'] = financial_data['Total Debt'] / financial_data['Debt plus Market Cap']
    financial_data['Cost of Debt After Tax'] = financial_data['Cost of Debt'] * (1 - financial_data['Effective Tax Rate'])
    financial_data['Weight of Equity'] = financial_data['Market Cap'] / financial_data['Debt plus Market Cap']

    # Calculate Cost of Equity
    financial_data['Cost of Equity'] = risk_free_rate + (financial_data['Beta'] * (market_return - risk_free_rate))

    # Calculate WACC
    financial_data['WACC'] = (financial_data['Weight of Debt'] * financial_data['Cost of Debt After Tax']) + (financial_data['Weight of Equity'] * financial_data['Cost of Equity'])

    # Calculate NOPAT
    financial_data['NOPAT'] = financial_data['Operating Income'] * (1 - financial_data['Effective Tax Rate']) 

    # Calculate ROIC
    financial_data['ROIC'] = financial_data['NOPAT'] / ((financial_data['Invested Capital 2023'] + financial_data['Invested Capital 2022']) / 2)

   

   # Calculate Free Cash Flow
    financial_data['Free Cash Flow'] = cash_flow_statement['Operating Cash Flow'].iloc[0] - abs(cash_flow_statement['Capital Expenditure'].iloc[0])

# Projected Cash Flows for 5 Years
    financial_data['Projected Cash Flows'] = []
    previous_cash_flow = financial_data['Free Cash Flow']
    for year in range(1, 6):
        projected_cash_flow = previous_cash_flow * (1 + growth_rate)
        financial_data[f'Projected Cash Flow Year {year}'] = projected_cash_flow
        financial_data['Projected Cash Flows'].append(projected_cash_flow)
        previous_cash_flow = projected_cash_flow

# Terminal Value Calculation
    if financial_data['WACC'] <= perpetual_growth_rate:
        st.error("WACC must be greater than the perpetual growth rate to calculate Terminal Value.")
    else:
        financial_data['Terminal Value'] = financial_data['Projected Cash Flow Year 5'] * (1 + perpetual_growth_rate) / (financial_data['WACC'] - perpetual_growth_rate)

# Enterprise Value Calculation
    financial_data['Enterprise Value'] = npf.npv(financial_data['WACC']/100, financial_data['Projected Cash Flows']) + financial_data['Terminal Value'] / ((1 + financial_data['WACC']/100) ** 5)

# Calculate Equity Value
    financial_data['Equity Value'] = financial_data['Enterprise Value'] - financial_data['Total Debt'] + financial_data['Cash and Cash Equivalents']

# Calculate Intrinsic Value 5 Year Projected Cash Flow
    if financial_data['Outstanding Shares'] == 0:
        st.error("Outstanding Shares cannot be zero.")
    else:
        financial_data['Intrinsic Value 5 Year Projected Cash Flow'] = financial_data['Equity Value'] / financial_data['Outstanding Shares']

    

    
    # Free Cash flow year 2023
    financial_data[f'Free Cash flow year {datetime.datetime.now().year -1 }'] = cash_flow_statement.loc[str(datetime.datetime.now().year -1 ), 'Free Cash Flow'].iloc[0]

    # Free Cash flow year 2022
    financial_data[f'Free Cash flow year {datetime.datetime.now().year -2 }'] = cash_flow_statement.loc[str(datetime.datetime.now().year -2 ), 'Free Cash Flow'].iloc[0]

    # Free Cash flow year 2021
    financial_data[f'Free Cash flow year {datetime.datetime.now().year -3 }'] = cash_flow_statement.loc[str(datetime.datetime.now().year -3 ), 'Free Cash Flow'].iloc[0]

    # Free Cash flow year 2020
    financial_data[f'Free Cash flow year {datetime.datetime.now().year -4 }'] = cash_flow_statement.loc[str(datetime.datetime.now().year -4 ), 'Free Cash Flow'].iloc[0]

        
    # Total Equity
    financial_data['Total Equity'] = balance_sheet['Total Equity Gross Minority Interest'].iloc[0]

    # Mean Cash Flow
    financial_data['Mean Cash Flow 4 years'] = (financial_data[f'Free Cash flow year {datetime.datetime.now().year -1 }']+ financial_data[f'Free Cash flow year {datetime.datetime.now().year -2 }']+ financial_data[f'Free Cash flow year {datetime.datetime.now().year -3 }']+financial_data[f'Free Cash flow year {datetime.datetime.now().year -4 }']) / 4
 
    # Value
    financial_data['Value'] = growth_multiple * financial_data['Mean Cash Flow 4 years'] + 0.8 * financial_data['Total Equity']

    # Intrinsic Value 
    financial_data['Intrinsic Value'] = financial_data['Value'] / financial_data['Outstanding Shares']    

    # Operating Margin
    financial_data['Operating Margin'] = financial_data['Operating Income'] / financial_data['Total Revenue']

    
    # Debt/EBITDA
    ebitda = income_statement['EBITDA'].iloc[0]
    financial_data['Debt/EBITDA'] = financial_data['Total Debt'] / ebitda if ebitda else None
    
    # P/E Ratio
    financial_data['P/E Ratio'] = stock.info.get('trailingPE', 'Not Found')
    
    # PEG Ratio
    financial_data['PEG Ratio'] = stock.info.get('pegRatio', 'Not Found')
    
    return financial_data

def fetch_piotroski(ticker):
    stock = yf.Ticker(ticker)
    balance_sheet = stock.balance_sheet.T
    income_statement = stock.financials.T
    cash_flow_statement = stock.cashflow.T

    # Initialize the scores with default values
    profitability_score = 0
    leverage_liquidity_source_of_funds_score = 0
    operating_efficiency_score = 0
    total_score = 0

    # Extract necessary fields
    financial_data = {}

    # Current and previous year data
    current_year = 0
    previous_year = 1

    try:
        # Profitability
        net_income = income_statement['Net Income'].iloc[current_year]
        total_assets = balance_sheet['Total Assets'].iloc[current_year]
        roa = net_income / total_assets

        operating_cash_flow = cash_flow_statement['Operating Cash Flow'].iloc[current_year]
        net_income_prev = income_statement['Net Income'].iloc[previous_year]
        total_assets_prev = balance_sheet['Total Assets'].iloc[previous_year]
        roa_prev = net_income_prev / total_assets_prev
        operating_cash_flow_prev = cash_flow_statement['Operating Cash Flow'].iloc[previous_year]

        # Leverage, Liquidity, and Source of Funds
        long_term_debt = balance_sheet['Long Term Debt'].iloc[current_year]
        long_term_debt_prev = balance_sheet['Long Term Debt'].iloc[previous_year]
        current_ratio = balance_sheet['Current Assets'].iloc[current_year] / balance_sheet['Current Liabilities'].iloc[current_year]
        current_ratio_prev = balance_sheet['Current Assets'].iloc[previous_year] / balance_sheet['Current Liabilities'].iloc[previous_year]
        
        gross_margin = income_statement['Gross Profit'].iloc[current_year] / income_statement['Total Revenue'].iloc[current_year]
        gross_margin_prev = income_statement['Gross Profit'].iloc[previous_year] / income_statement['Total Revenue'].iloc[previous_year]
        asset_turnover = income_statement['Total Revenue'].iloc[current_year] / total_assets
        asset_turnover_prev = income_statement['Total Revenue'].iloc[previous_year] / total_assets_prev

        # Get shares outstanding
        shares_outstanding = stock.info.get('sharesOutstanding', 'Not Found')

        # Calculate F-Score components
        profitability_score = 0
        leverage_liquidity_source_of_funds_score = 0
        operating_efficiency_score = 0

        # Profitability (out of 4)
        profitability_score += int(roa > 0)                             # Positive ROA
        profitability_score += int(operating_cash_flow > 0)            # Positive Operating Cash Flow
        profitability_score += int(roa > roa_prev)                     # ROA improved
        profitability_score += int(operating_cash_flow > net_income)   # Operating Cash Flow greater than Net Income

        # Leverage, Liquidity, and Source of Funds (out of 3)
        leverage_liquidity_source_of_funds_score += int(long_term_debt < long_term_debt_prev)     # Decrease in Long-term Debt
        leverage_liquidity_source_of_funds_score += int(current_ratio > current_ratio_prev)       # Improvement in Current Ratio
        leverage_liquidity_source_of_funds_score += int(shares_outstanding == shares_outstanding) # Check historical shares (may need adjustment)

        # Operating Efficiency (out of 2)
        operating_efficiency_score += int(gross_margin > gross_margin_prev)     # Improvement in Gross Margin
        operating_efficiency_score += int(asset_turnover > asset_turnover_prev) # Improvement in Asset Turnover

        # Calculate total Piotroski F-Score out of 9
        total_score = profitability_score + leverage_liquidity_source_of_funds_score + operating_efficiency_score

    except KeyError as e:
        print(f"KeyError: {e} - Check if all necessary fields are available in the financial statements")
    except IndexError as e:
        print(f"IndexError: {e} - Check if there is sufficient historical data")

    # Create DataFrames for the scores
    profitability_df = pd.DataFrame({
        'Category': ['Profitability'],
        'Score': [f"{profitability_score}/4"],
        'Piotroski Score': [profitability_score]
    })

    leverage_liquidity_source_of_funds_df = pd.DataFrame({
        'Category': ['Leverage, Liquidity, and Source of Funds'],
        'Score': [f"{leverage_liquidity_source_of_funds_score}/3"],
        'Piotroski Score': [leverage_liquidity_source_of_funds_score]
    })

    operating_efficiency_df = pd.DataFrame({
        'Category': ['Operating Efficiency'],
        'Score': [f"{operating_efficiency_score}/2"],
        'Piotroski Score': [operating_efficiency_score]
    })

    total_score_df = pd.DataFrame({
        'Category': ['Total Piotroski Score'],
        'Score': [f"{total_score}/9"],
        'Piotroski Score': [total_score]
    })

    # Concatenate all DataFrames
    scores_df = pd.concat([profitability_df, leverage_liquidity_source_of_funds_df, operating_efficiency_df, total_score_df], ignore_index=True)
    
    return scores_df
    


# Streamlit app
st.title('Financial Data and Valuation')

# Inputs
ticker = st.text_input('Enter Stock Ticker Symbol', 'AAPL')
growth_assumption = st.slider('Enter Growth Assumption (%)', min_value=1, max_value=15, value=15)

if ticker and growth_assumption:
    try:
        # Fetch financial data
        financial_data = fetch_financial_data(ticker, growth_assumption)

        # Check if financial data is available
        if financial_data:
            # Convert financial data to DataFrame
            financial_df = pd.DataFrame(list(financial_data.items()), columns=['Key', 'Value'])

            # Display the financial data
            st.write(f"Financial data for {ticker}:")
            st.dataframe(financial_df)
        else:
            st.error(f"No financial data found for ticker {ticker}.")

        # Fetch Piotroski F-Score
        piotroski_scores_df = fetch_piotroski(ticker)

        # Check if Piotroski F-Score data is available
        if not piotroski_scores_df.empty:
            # Display Piotroski F-Score
            st.write(f"Piotroski F-Score for {ticker}:")
            st.dataframe(piotroski_scores_df)
        else:
            st.error(f"No Piotroski F-Score data found for ticker {ticker}.")

    except Exception as e:
        st.error(f"An error occurred: {e}")

    # Custom CSS for positioning text
custom_css = """
<style>
.bottom-right {
    position: fixed;
    bottom: 10px;
    right: 80px;
    background-color: rgba(255, 255, 255, 0.8);
    padding: 10px;
    border-radius: 5px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}
</style>
"""

# Custom HTML for the text
custom_html = """
<div class="bottom-right">
    © 2024 Nikolai ROPA
</div>
"""

# Injecting CSS and HTML into the Streamlit app
st.markdown(custom_css, unsafe_allow_html=True)
st.markdown(custom_html, unsafe_allow_html=True)
