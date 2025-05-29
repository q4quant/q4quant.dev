import yfinance as yf
import pandas as pd

# Fetch dividend info for a given symbol
def fetch_dividend_info(symbol):
    stock = yf.Ticker(symbol)
    info = stock.info
    
    # Get dividend rate and yield
    dividend_rate = info.get('dividendRate', 0)
    dividend_yield = info.get('dividendYield', 0)
    
    # Determine frequency based on dividend rate and yield
    if dividend_rate and dividend_yield:
        # Get the last 4 dividend payments
        dividends = stock.dividends
        if not dividends.empty:
            last_4_dividends = dividends.tail(4)
            if len(last_4_dividends) >= 2:
                avg_days = (last_4_dividends.index[-1] - last_4_dividends.index[0]).days / (len(last_4_dividends) - 1)
                match avg_days:
                    case _ if avg_days <= 35:
                        frequency = "Monthly"
                        multiplier = 1
                    case _ if avg_days <= 95:
                        frequency = "Quarterly"
                        multiplier = 3
                    case _ if avg_days <= 185:
                        frequency = "Semi-annual"
                        multiplier = 6
                    case _:
                        frequency = "Annual"
                        multiplier = 12
            else:
                frequency = "Unknown"
                multiplier = 12
        else:
            frequency = "Unknown"
            multiplier = 12
    else:
        frequency = "No dividend"
        multiplier = 12
    
    return {
        'dividend_yield': dividend_yield,
        'frequency': frequency,
        'multiplier': multiplier
    }

# Calculate required investment for a target monthly dividend
def calculate_required_investment(monthly_target, dividend_info):
    if dividend_info['dividend_yield'] == 'N/A' or dividend_info['dividend_yield'] is None:
        return 'N/A'
    adjusted_monthly = monthly_target * dividend_info['multiplier']
    monthly_yield = dividend_info['dividend_yield'] / 12
    required_investment = (adjusted_monthly / monthly_yield) * 100
    return round(required_investment, 2)

# Generate the dividend schedule
def generate_dividend_schedule(monthly_target, frequency, multiplier, enable_drip, initial_investment, dividend_yield=None):
    months = []
    payments = []
    running_totals = []
    total_investments = []
    current_investment = initial_investment
    running_total = 0

    # Determine the number of payments per year
    if frequency == "Monthly":
        periods = 12
    elif frequency == "Quarterly":
        periods = 4
    elif frequency == "Semi-annual":
        periods = 2
    elif frequency == "Annual":
        periods = 1
    else:
        periods = 12

    period_interval = 12 // periods

    for i in range(12):
        months.append(f"Month {i}")
        if i == 0:
            payment = 0
            running_total = 0
        else:
            if enable_drip and dividend_yield is not None:
                annual_yield = dividend_yield
                period_yield = annual_yield / periods
                if i % period_interval == 0:
                    payment = current_investment * (period_yield / 100)
                else:
                    payment = 0
            else:
                match frequency:
                    case "Monthly":
                        payment = monthly_target
                    case "Quarterly":
                        payment = monthly_target * 3 if i % 3 == 0 else 0
                    case "Semi-annual":
                        payment = monthly_target * 6 if i % 6 == 0 else 0
                    case "Annual":
                        payment = monthly_target * 12 if i == 0 else 0
                    case _:
                        payment = 0
            running_total += payment
        payments.append(payment)
        running_totals.append(running_total)
        if i == 0:
            total_investments.append(current_investment)
        else:
            if enable_drip:
                current_investment += payments[i-1]
            total_investments.append(current_investment)
    df = pd.DataFrame({
        'Month': months,
        'Payment': [f"${payment:,.2f}" for payment in payments],
        'Running Total': [f"${total:,.2f}" for total in running_totals],
        'Total Investment': [f"${ti:,.2f}" for ti in total_investments]
    })
    return df 