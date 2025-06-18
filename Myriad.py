import streamlit as st
import pandas as pd

# Sheet parameters DataFrame
sheet_params = pd.DataFrame({
    'SheetName': ['Equities', 'FEXD', 'Bonds', 'FX', 'Energy', 'Metals', 'Crops', 'Softs'],
    'Hedge_skiprows': [1, 1, 1, 1, 1, 1, 1, 1],
    'Hedge_nrows': [17, 8, 19, 9, 9, 6, 9, 10],
    'Price_skiprows': [20, 11, 23, 12, 12, 8, 12, 12],
    'Price_nrows': [17, 8, 19, 9, 9, 6, 9, 10],
    'LastProduct': ['SXF', 'FEXD24', 'BAX', 'UKNG', 'UKNG', 'COPPER', 'RICE', 'LUMBER']
})

# File path to your Excel file
file_path = "Spread Ratios.xlsx"

# Helper to get sheet parameters
def get_sheet_params(sheet_name):
    row = sheet_params[sheet_params['SheetName'] == sheet_name]
    if row.empty:
        st.error(f"Sheet name '{sheet_name}' not found in parameters.")
        st.stop()
    return row.iloc[0]

# Helper to get product list for dropdowns
def get_product_list(sheet_name):
    params = get_sheet_params(sheet_name)
    hedge_df = pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        skiprows=int(params['Hedge_skiprows']),
        nrows=int(params['Hedge_nrows'])
    )
    hedge_df.columns = [str(c).strip() for c in hedge_df.columns]
    products = [col for col in hedge_df.columns if col != 'Product']
    if 'Product' in hedge_df.columns:
        products += hedge_df['Product'].dropna().unique().tolist()
    products = sorted(set([str(p).strip() for p in products if pd.notna(p) and str(p).strip() != '']))
    return products

# Helper to fetch ratios with N/A handling
def get_ratios(product1, product2, sheet_name):
    params = get_sheet_params(sheet_name)
    # Load DataFrames
    hedge_df = pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        skiprows=int(params['Hedge_skiprows']),
        nrows=int(params['Hedge_nrows'])
    )
    price_df = pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        skiprows=int(params['Price_skiprows']),
        nrows=int(params['Price_nrows'])
    )
    last_product = params['LastProduct']
    cols_to_keep = hedge_df.columns[:hedge_df.columns.get_loc(last_product)+1]
    hedge_df = hedge_df[cols_to_keep]
    price_df = price_df[cols_to_keep]
    hedge_df.columns = hedge_df.columns.str.strip()
    hedge_df['Product'] = hedge_df['Product'].astype(str).str.strip()
    price_df.columns = price_df.columns.str.strip()
    price_df['Product'] = price_df['Product'].astype(str).str.strip()

    def fetch_ratio(df, prod1, prod2):
        idx1 = df.index[df['Product'] == prod1].tolist()
        idx2 = df.index[df['Product'] == prod2].tolist()
        if not idx1 or not idx2:
            return 'N/A'
        row_idx = idx1[0]
        col_idx = df.columns.get_loc(prod2)
        if col_idx > 0 and col_idx > row_idx:
            val = df.iloc[row_idx, col_idx]
            if pd.isna(val) or str(val).strip().upper() in ['N/A', 'NA', '']:
                return 'N/A'
            return val
        row_idx_rev = idx2[0]
        col_idx_rev = df.columns.get_loc(prod1)
        if col_idx_rev > 0 and col_idx_rev > row_idx_rev:
            val = df.iloc[row_idx_rev, col_idx_rev]
            if pd.isna(val) or str(val).strip().upper() in ['N/A', 'NA', '']:
                return 'N/A'
            return val
        return 'N/A'

    hedge_ratio = fetch_ratio(hedge_df, product1, product2)
    price_ratio = fetch_ratio(price_df, product1, product2)
    return hedge_ratio, price_ratio

# --- Streamlit UI ---

st.title("Hedge & Price Ratio Lookup")

# Dropdown 1: Select sheet/product type
sheet_name = st.selectbox("Select Product Type (Sheet):", sheet_params['SheetName'].tolist())

# Dropdowns 2 & 3: Select products (dependent on sheet)
products = get_product_list(sheet_name)
product1 = st.selectbox("Select First Product:", products)
product2 = st.selectbox("Select Second Product:", products)

# Show ratios when both products are selected and not the same
if product1 and product2 and product1 != product2:
    hedge_ratio, price_ratio = get_ratios(product1, product2, sheet_name)
    st.markdown(f"### Results for **{product1}** and **{product2}** in **{sheet_name}**")
    st.write(f"**Hedge Ratio:** {hedge_ratio}")
    st.write(f"**Price Ratio:** {price_ratio}")
elif product1 == product2:
    st.info("Please select two different products.")

