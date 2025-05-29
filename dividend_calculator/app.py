import streamlit as st
import pandas as pd
from dividend_utils import fetch_dividend_info, calculate_required_investment, generate_dividend_schedule

st.set_page_config(layout="wide")

@st.cache_data
def get_dividend_info(symbol):
    return fetch_dividend_info(symbol)

# with st.sidebar:
#     st.title('Dividend Calculator')

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader('Dividend Yield Lookup')
    symbol = st.text_input('Enter a stock symbol (e.g., AAPL)')
    if symbol:
        dividend_info = get_dividend_info(symbol)
        st.write(f"**Dividend Yield:** {dividend_info['dividend_yield']}")
        
        # Show warning popup if frequency is unknown or no dividend
        if dividend_info['frequency'] in ["Unknown", "No dividend"]:
            st.warning("The payment frequency could not be determined automatically. Please select it manually.")
            frequency = st.selectbox(
                "Select Dividend Payment Frequency",
                ["Monthly", "Quarterly", "Semi-annual", "Annual"],
                index=3  # Default to Annual
            )
            # Update multiplier based on selected frequency
            multiplier_map = {
                "Monthly": 1,
                "Quarterly": 3,
                "Semi-annual": 6,
                "Annual": 12
            }
            dividend_info['frequency'] = frequency
            dividend_info['multiplier'] = multiplier_map[frequency]
        else:
            st.write(f"**Payment Frequency:** {dividend_info['frequency']}")

with col2:
    st.subheader('Investment Calculator')
    
    # Calculator mode selection
    mode = st.selectbox('Calculator Mode', ['Required Investment', 'Investment Outcome'])
    
    match mode:
        case 'Required Investment':
            monthly_target = st.number_input('Target Monthly Dividend ($)', min_value=0.0, step=100.0)
            enable_drip = st.checkbox('Enable DRIP (Dividend Reinvestment Plan)', value=False)
            if symbol and monthly_target > 0:
                required_investment = calculate_required_investment(monthly_target, dividend_info)
                if required_investment != 'N/A':
                    st.write(f"**Required Investment:** ${required_investment:,.2f}")
                    st.write(f"**Annual Dividend Income:** ${monthly_target * 12:,.2f}")
                    if dividend_info['frequency'] != "Monthly":
                        st.write(f"*Note: Since dividends are paid {dividend_info['frequency'].lower()}, you'll receive ${monthly_target * dividend_info['multiplier']:,.2f} per payment*")
                    # Show dividend schedule
                    st.write("### Dividend Schedule")
                    schedule_df = generate_dividend_schedule(monthly_target, dividend_info['frequency'], dividend_info['multiplier'], enable_drip, required_investment, dividend_info['dividend_yield'])
                    st.dataframe(schedule_df, hide_index=True, height=len(schedule_df) * 35 + 38)
                else:
                    st.write("Please enter a valid stock symbol to calculate required investment")
        case 'Investment Outcome':
            initial_investment = st.number_input('Initial Investment ($)', min_value=0.0, step=100.0)
            enable_drip = st.checkbox('Enable DRIP (Dividend Reinvestment Plan)', value=False)
            if symbol and initial_investment > 0:
                # Calculate monthly target based on initial investment and yield
                annual_yield = dividend_info['dividend_yield']
                if annual_yield and annual_yield > 0:
                    # Estimate monthly target for schedule display (for non-DRIP)
                    monthly_target = (initial_investment * (annual_yield / 100)) / 12
                    st.write(f"**Estimated Monthly Dividend:** ${monthly_target:,.2f}")
                    st.write(f"**Estimated Annual Dividend Income:** ${monthly_target * 12:,.2f}")
                    if dividend_info['frequency'] != "Monthly":
                        st.write(f"*Note: Since dividends are paid {dividend_info['frequency'].lower()}, you'll receive ${monthly_target * dividend_info['multiplier']:,.2f} per payment*")
                    # Show dividend schedule
                    st.write("### Dividend Schedule")
                    schedule_df = generate_dividend_schedule(monthly_target, dividend_info['frequency'], dividend_info['multiplier'], enable_drip, initial_investment, dividend_info['dividend_yield'])
                    st.dataframe(schedule_df, hide_index=True, height=len(schedule_df) * 35 + 38)
                else:
                    st.write("This stock does not pay a dividend.")
