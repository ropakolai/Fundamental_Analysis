import streamlit as st
import yfinance as yf
import pandas as pd
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
    perpetual_growth_rate = 0.025
    growth_multiple = 8.3459 * (1.07) ** (growth_assumption - 4)

    # Total Debt
    financial_data['Total Debt'] = balance_sheet['Total Debt'].iloc[0]

    # Cash and Cash Equivalents
    financial_data['Cash and Cash Equivalents'] = balance_sheet['Cash And Cash Equivalents'].iloc[0]

    # Invested Capital for 2023 and 2022
    financial_data['Invested Capital 2023'] = balance_sheet['Total Assets'].iloc[0] - balance_sheet['Total Liabilities Net Minority Interest'].iloc[0]
    financial_data['Invested Capital 2022'] = balance_sheet['Total Assets'].iloc[1] - balance_sheet['Total Liabilities Net Minority Interest'].iloc[1]

    # Interest Expense
    financial_data['Interest Expense'] = income_statement['Interest Expense'].iloc[0]

    # Income Tax Expense
    financial_data['Tax Provision'] = income_statement['Tax Provision'].iloc[0]

    # Income Before Tax
    financial_data['Pretax Income'] = income_statement['Pretax Income'].iloc[0]

    # Operating Income
    financial_data['Operating Income'] = income_statement['Operating Income'].iloc[0]

    # Calculate Weight of Debt
    financial_data['Effective Tax Rate'] = financial_data['Tax Provision'] / financial_data['Pretax Income']
    financial_data['Cost of Debt'] = financial_data['Interest Expense'] / financial_data['Total Debt']

    # Market Cap
    financial_data['Market Cap'] = stock.info['marketCap']

    # Beta
    financial_data['Beta'] = stock.info['beta']

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
    financial_data['Free Cash Flow'] = financial_data['Operating Cash Flow'] / financial_data['Capital Expenditure']

    # Calculate Project Cash flow for 5 years
    projected_cash_flows = []
    cash_flow = financial_data['Free Cash Flow']
    for _ in range(5):
        cash_flow = cash_flow * (1 + growth_rate)
        projected_cash_flows.append(cash_flow)
    
    financial_data['Projected Cash Flow Year 5'] = projected_cash_flows[-1]
    financial_data['Terminal Value'] =  financial_data['Projected Cash Flow Year 5'] * (1 + perpetual_growth_rate) / (financial_data['WACC'] - perpetual_growth_rate)
    
    # Enterprise Value Calculation
    financial_data['Enterprise Value'] = financial_data['Market Cap'] + financial_data['Total Debt'] - financial_data['Cash and Cash Equivalents']

    # Calculate Equity Value
    financial_data['Equity Value'] = financial_data['Enterprise Value'] - financial_data['Total Debt'] + financial_data['Cash and Cash Equivalents']
    
    # Calculate Intrinsic Value 5 Year Projected Cash Flow
    financial_data['Intrinsic Value 5 Year Projected Cash Flow'] = financial_data['Equity Value'] / financial_data['Outstanding Shares']

    
    #Free Cash flow year 2023
    financial_data[f'Free Cash flow year {datetime.datetime.now().year -1 }'] = cash_flow_statement.loc[str(datetime.datetime.now().year -1 ), 'Free Cash Flow'].iloc[0]

    #Free Cash flow year 2022
    financial_data[f'Free Cash flow year {datetime.datetime.now().year -2 }'] = cash_flow_statement.loc[str(datetime.datetime.now().year -2 ), 'Free Cash Flow'].iloc[0]

    #Free Cash flow year 2021
    financial_data[f'Free Cash flow year {datetime.datetime.now().year -3 }'] = cash_flow_statement.loc[str(datetime.datetime.now().year -3 ), 'Free Cash Flow'].iloc[0]

    #Free Cash flow year 2020
    financial_data[f'Free Cash flow year {datetime.datetime.now().year -4 }'] = cash_flow_statement.loc[str(datetime.datetime.now().year -4 ), 'Free Cash Flow'].iloc[0]

    #Total Equity
    financial_data['Total Equity'] = balance_sheet['Total Equity Gross Minority Interest'].iloc[0]

    #Mean Cash Flow
    financial_data['Mean Cash Flow 4 years'] = (financial_data[f'Free Cash flow year {datetime.datetime.now().year -1 }']+ financial_data[f'Free Cash flow year {datetime.datetime.now().year -2 }']+ financial_data[f'Free Cash flow year {datetime.datetime.now().year -3 }']+financial_data[f'Free Cash flow year {datetime.datetime.now().year -4 }']) / 4
 
    #Value
    financial_data['Value'] = growth_multiple * financial_data['Mean Cash Flow 4 years'] + 0.8 * financial_data['Total Equity']

    #Intrinsic Value 
    financial_data['Intrinsic Value'] = financial_data['Value'] / financial_data['Outstanding Shares']    
    return financial_data

# Streamlit app
st.title('Financial Data and Valuation')

# Inputs
ticker = st.text_input('Enter Stock Ticker Symbol', 'AAPL')
growth_assumption = st.slider('Enter Growth Assumption (years)', min_value=1, max_value=30, value=15)

if ticker and growth_assumption:
    # Fetch financial data
    financial_data = fetch_financial_data(ticker, growth_assumption)

    # Convert financial data to DataFrame
    df = pd.DataFrame(list(financial_data.items()), columns=['Key', 'Value'])

    # Display the data
    st.write(f"Financial data for {ticker}:")
    st.dataframe(df)
