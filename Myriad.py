import streamlit as st
import pandas as pd

# Load the Excel file
excel_path = "Spread Ratios.xlsx"
excel_file = pd.ExcelFile(excel_path)

# Load product list
products_df = excel_file.parse("All Product Stellar")
product_list = products_df.iloc[:, 0].dropna().tolist()

# Load all category sheets
category_sheets = [s for s in excel_file.sheet_names if s != "All Product Stellar"]
category_data = {sheet: excel_file.parse(sheet, header=None) for sheet in category_sheets}

# Build product-to-category mapping
product_category_map = {}
for sheet, df in category_data.items():
    hedge_start = df[df[0] == "HEDGE (TRADE) RATIO:"].index
    chart_start = df[df[0] == "PRICE (CHART) RATIO:"].index
    if len(hedge_start) == 0 or len(chart_start) == 0:
        continue

    hedge_start = hedge_start[0] + 1
    chart_start = chart_start[0] + 1
    hedge_end = chart_start - 2

    try:
        hedge_df = df.iloc[hedge_start:hedge_end].dropna(how='all', axis=1).reset_index(drop=True)
        hedge_df.columns = hedge_df.iloc[0]
        hedge_df = hedge_df[1:]
        row_headers = hedge_df.iloc[:, 0].dropna().unique().tolist()
        col_headers = hedge_df.columns[1:].tolist()
        all_products = set(row_headers + col_headers)
        for product in all_products:
            product_category_map[product] = sheet
    except Exception:
        continue

# Streamlit UI
st.title("Spread Ratio Dashboard")
product1 = st.selectbox("Select Product 1", product_list)
product2 = st.selectbox("Select Product 2", product_list)

category1 = product_category_map.get(product1)
category2 = product_category_map.get(product2)

def bidirectional_lookup(df, product1, product2):
    try:
        return df.at[product1, product2]
    except KeyError:
        try:
            return df.at[product2, product1]
        except KeyError:
            return "null"

def find_ratios(product1, product2, sheet_name):
    df = category_data[sheet_name]

    hedge_start = df[df[0] == "HEDGE (TRADE) RATIO:"].index[0] + 1
    chart_start = df[df[0] == "PRICE (CHART) RATIO:"].index[0] + 1
    hedge_end = chart_start - 2

    hedge_df = df.iloc[hedge_start:hedge_end].dropna(how='all', axis=1).reset_index(drop=True)
    chart_df = df.iloc[chart_start:].dropna(how='all', axis=1).reset_index(drop=True)

    hedge_df.columns = hedge_df.iloc[0]
    hedge_df = hedge_df[1:].set_index(hedge_df.columns[0])
    chart_df.columns = chart_df.iloc[0]
    chart_df = chart_df[1:].set_index(chart_df.columns[0])

    hedge_value = bidirectional_lookup(hedge_df, product1, product2)
    chart_value = bidirectional_lookup(chart_df, product1, product2)

    return hedge_value, chart_value

# Main logic
if category1 and category2 and category1 == category2:
    hedge_ratio, chart_ratio = find_ratios(product1, product2, category1)
    st.markdown(f"### Category: `{category1}`")
else:
    hedge_ratio, chart_ratio = "null", "null"
    st.markdown("### Products are from different categories.")

st.metric("Hedge Ratio", hedge_ratio)
st.metric("Chart Ratio", chart_ratio)

