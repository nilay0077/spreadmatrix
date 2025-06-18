import streamlit as st
import pandas as pd

# Load the Excel file
excel_path = "Spread Ratios.xlsx"
excel_file = pd.ExcelFile(excel_path)

# Load products list
products_df = excel_file.parse("All Product Stellar")
product_list = products_df.iloc[:, 0].dropna().tolist()

# Load all category sheets except the product list
category_sheets = [s for s in excel_file.sheet_names if s != "All Product Stellar"]
category_data = {sheet: excel_file.parse(sheet, header=None) for sheet in category_sheets}

st.title("Spread Ratio Dashboard")

# Dropdowns for product selection
product1 = st.selectbox("Select Product 1", product_list)
product2 = st.selectbox("Select Product 2", product_list)

# Attempt to find both products in one of the category sheets
def find_ratios(product1, product2):
    for sheet, df in category_data.items():
        # Find hedge matrix
        hedge_start = df[df[0] == "HEDGE (TRADE) RATIO:"].index
        chart_start = df[df[0] == "PRICE (CHART) RATIO:"].index

        if len(hedge_start) == 0 or len(chart_start) == 0:
            continue

        hedge_start = hedge_start[0] + 1
        chart_start = chart_start[0] + 1

        hedge_end = chart_start - 2
        chart_end = len(df)

        hedge_df = df.iloc[hedge_start:hedge_end].dropna(how='all', axis=1).reset_index(drop=True)
        chart_df = df.iloc[chart_start:].dropna(how='all', axis=1).reset_index(drop=True)

        try:
            hedge_df.columns = hedge_df.iloc[0]
            hedge_df = hedge_df[1:].set_index(hedge_df.columns[0])

            chart_df.columns = chart_df.iloc[0]
            chart_df = chart_df[1:].set_index(chart_df.columns[0])

            hedge_value = hedge_df.loc[product1, product2]
            chart_value = chart_df.loc[product1, product2]

            return sheet, hedge_value, chart_value

        except Exception:
            continue

    return None, None, None

# Run lookup
category, hedge_ratio, chart_ratio = find_ratios(product1, product2)

if category:
    st.markdown(f"### Category Found: `{category}`")
    st.metric("Hedge Ratio", hedge_ratio)
    st.metric("Chart Ratio", chart_ratio)
else:
    st.warning("No category sheet found with both selected products.")
