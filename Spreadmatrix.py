import streamlit as st
import pandas as pd

# Load the data from Excel (you'll need to adjust the path)
@st.cache_data
def load_data():
    # This is a representation of your Excel data
    hedge_ratio_data = {
        'Product': ['FESX', 'DAX', 'SMI', 'FTSE', 'CAC', 'S&P', 'NASDAQ', 'DOW', 'RTY', 'MDAX', 'EMD', 'AEX', 'FVS', 'VIX', 'FESB', 'SXF'],
        'FESX': [1, 7.8, None, 1.4, None, 0.8, 6.3, 2.5, 0.2, 1, None, None, None, None, 0.2, None],
        'DAX': [None, 1, None, 0.2, None, 0.1, 0.8, 0.3, 0, 0.1, None, None, None, None, 0, None],
        'SMI': [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
        'FTSE': [None, None, None, 1, None, 0.6, 4.5, 1.7, 0.2, 0.7, None, None, None, None, 0.1, None],
        'CAC': [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
        'S&P': [None, None, None, None, None, 1, 7.6, 3, 0.3, 1.3, None, None, None, None, 0.2, None],
        'NASDAQ': [None, None, None, None, None, None, 1, 0.4, 0, 0.2, None, None, None, None, 0, None],
        'DOW': [None, None, None, None, None, None, None, 1, 0.1, 0.4, None, None, None, None, 0.1, None],
        'RTY': [None, None, None, None, None, None, None, None, 1, 4.8, None, None, None, None, 0.9, None],
        'MDAX': [None, None, None, None, None, None, None, None, None, 1, None, None, None, None, 0.2, None],
        'EMD': [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
        'AEX': [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
        'FVS': [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
        'VIX': [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
        'FESB': [None, None, None, None, None, None, None, None, None, None, None, None, None, None, 1, None],
        'SXF': [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
    }
    
    chart_ratio_data = {
        'Product': ['FESX', 'DAX', 'SMI', 'FTSE', 'CAC', 'S&P', 'NASDAQ', 'DOW', 'RTY', 'MDAX', 'EMD', 'AEX', 'FVS', 'VIX', 'FESB', 'SXF'],
        'FESX': [1, 3.1, None, 1.1, None, 0.7, 3.4, 5.3, 0.5, 10.5, None, None, None, None, 0, None],
        'DAX': [None, 1, None, 0.4, None, 0.2, 1.1, 1.7, 0.2, 3.4, None, None, None, None, 0, None],
        'SMI': [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
        'FTSE': [None, None, None, 1, None, 0.6, 3.1, 4.7, 0.4, 9.3, None, None, None, None, 0, None],
        'CAC': [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
        'S&P': [None, None, None, None, None, 1, 4.8, 7.4, 0.7, 14.6, None, None, None, None, 0.1, None],
        'NASDAQ': [None, None, None, None, None, None, 1, 1.6, 0.1, 3.1, None, None, None, None, 0, None],
        'DOW': [None, None, None, None, None, None, None, 1, 0.1, 2, None, None, None, None, 0, None],
        'RTY': [None, None, None, None, None, None, None, None, 1, 22.2, None, None, None, None, 0.1, None],
        'MDAX': [None, None, None, None, None, None, None, None, None, 1, None, None, None, None, 0, None],
        'EMD': [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
        'AEX': [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
        'FVS': [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
        'VIX': [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
        'FESB': [None, None, None, None, None, None, None, None, None, None, None, None, None, None, 1, None],
        'SXF': [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
    }
    
    hedge_df = pd.DataFrame(hedge_ratio_data).set_index('Product')
    chart_df = pd.DataFrame(chart_ratio_data).set_index('Product')
    
    return hedge_df, chart_df

hedge_df, chart_df = load_data()
products = hedge_df.index.tolist()

# Streamlit app
st.title("Spread Ratio Dashboard")

# Product selection
col1, col2 = st.columns(2)
with col1:
    product1 = st.selectbox("Select Product 1", products, index=0)
with col2:
    product2 = st.selectbox("Select Product 2", products, index=1)

st.markdown("---")

# Get ratios
def get_ratio(df, p1, p2):
    try:
        # Check both directions since the matrix isn't symmetric
        ratio = df.loc[p1, p2]
        if pd.isna(ratio):
            ratio = df.loc[p2, p1]
        return ratio if not pd.isna(ratio) else "null"
    except:
        return "null"

hedge_ratio = get_ratio(hedge_df, product1, product2)
chart_ratio = get_ratio(chart_df, product1, product2)

# Display results
st.subheader(f"Results for {product1} vs {product2}")

col1, col2 = st.columns(2)
with col1:
    st.metric("Hedge Ratio", hedge_ratio)
with col2:
    st.metric("Chart Ratio", chart_ratio)

# Additional information
if hedge_ratio == "null" and chart_ratio == "null":
    st.warning("No ratio data available for this product pair")
elif product1 == product2:
    st.info("You've selected the same product for both selections")