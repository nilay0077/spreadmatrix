import streamlit as st
import pandas as pd
import requests

# ---- Utility Functions ----
def clean_columns(df):
    return df.loc[:, [col for col in df.columns if not str(col).startswith("Unnamed") and str(col).strip() != ""]]

def clean_rows(df):
    if 'Product' in df.columns:
        df = df[df['Product'].notna()]
        df = df[~df['Product'].astype(str).str.startswith("Unnamed")]
        df = df[df['Product'].astype(str).str.strip() != ""]
    return df

def fetch_ratio(df, prod1, prod2):
    try:
        row = df[df['Product'] == prod1]
        if not row.empty and prod2 in df.columns:
            val = row.iloc[0][prod2]
            if pd.isna(val) or str(val).strip().upper() in ['N/A', 'NA', '']:
                return 'N/A'
            return val
        return 'N/A'
    except Exception:
        return 'N/A'

def get_ratios_api(product1, product2, hedge_df, price_df):
    hedge_ratio = fetch_ratio(hedge_df, product1, product2)
    price_ratio = fetch_ratio(price_df, product1, product2)
    return hedge_ratio, price_ratio

def round_ratio(val, decimals=1):
    try:
        if isinstance(val, (int, float)) and not pd.isna(val):
            return round(val, decimals)
        return val
    except Exception:
        return val

# ---- Fetch Data from API ----
@st.cache_data(ttl=60)
def load_data():
    url = "http://127.0.0.1:8000/data"  # <-- Local FastAPI endpoint
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        json_data = response.json()

        hedge_df = pd.DataFrame(json_data["hedge_ratios"])
        price_df = pd.DataFrame(json_data["price_ratios"])

        hedge_df = clean_columns(hedge_df)
        price_df = clean_columns(price_df)
        hedge_df = clean_rows(hedge_df)
        price_df = clean_rows(price_df)

        return hedge_df, price_df
    except Exception as e:
        st.error(f"Failed to fetch API data: {e}")
        st.stop()

# ---- Streamlit UI ----
st.title("📊 Spread Ratio Dashboard (API Version)")

if st.button("🔄 Reload Data"):
    st.cache_data.clear()

hedge_df, price_df = load_data()
products = hedge_df['Product'].tolist()

product1 = st.selectbox("Select Product 1:", products, key="prod1")
product2 = st.selectbox("Select Product 2:", products, key="prod2")

if product1 and product2 and product1 != product2:
    hedge_ratio, price_ratio = get_ratios_api(product1, product2, hedge_df, price_df)
    hedge_ratio_rounded = round_ratio(hedge_ratio)
    price_ratio_rounded = round_ratio(price_ratio)
    
    st.markdown(f"### 🔎 Results for **{product1}** and **{product2}**")
    st.write(f"**Hedge Ratio:** `{hedge_ratio_rounded}`")
    st.write(f"**Price Ratio:** `{price_ratio_rounded}`")
elif product1 == product2:
    st.info("Please select two different products.")
