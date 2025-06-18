import streamlit as st
import pandas as pd

# Load the Excel file
excel_path = "Spread Ratios.xlsx"
excel_file = pd.ExcelFile(excel_path)

# Load products list
products_df = excel_file.parse("All Product Stellar")
product_list = products_df.iloc[:, 0].dropna().tolist()  # Assuming first column contains product names

# Load all category sheets
category_sheets = [sheet for sheet in excel_file.sheet_names if sheet not in ["All Product Stellar"]]
category_data = {sheet: excel_file.parse(sheet, header=None) for sheet in category_sheets}

st.title("Spread Ratio Dashboard")

# Dropdowns for product selection
product1 = st.selectbox("Select Product 1", product_list)
product2 = st.selectbox("Select Product 2", product_list)

# Find category that contains both products
def find_common_category(product1, product2):
    for sheet, df in category_data.items():
        try:
            header_row_index = df[df.apply(lambda row: row.astype(str).str.contains(product1).any(), axis=1)].index[0]
            if product2 in df.iloc[header_row_index, :].values or product2 in df.iloc[:, 0].values:
                return sheet, df, header_row_index
        except IndexError:
            continue
    return None, None, None

category, df, header_index = find_common_category(product1, product2)

if category:
    st.markdown(f"### Category Found: `{category}`")

    # Assume first matrix is chart ratio, second is hedge ratio, separated by an empty row
    split_index = df[df.isnull().all(axis=1)].index[0]  # Split point between matrices
    chart_ratio_df = df.iloc[header_index:split_index].reset_index(drop=True)
    hedge_ratio_df = df.iloc[split_index+1:].reset_index(drop=True)

    # Extract ratio values
    try:
        chart_ratio = chart_ratio_df.set_index(chart_ratio_df.columns[0]).loc[product1, product2]
    except KeyError:
        chart_ratio = "Not found"

    try:
        hedge_ratio = hedge_ratio_df.set_index(hedge_ratio_df.columns[0]).loc[product1, product2]
    except KeyError:
        hedge_ratio = "Not found"

    st.metric("Chart Ratio", chart_ratio)
    st.metric("Hedge Ratio", hedge_ratio)
else:
    st.warning("No common category sheet found containing both selected products.")

