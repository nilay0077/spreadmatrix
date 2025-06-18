import streamlit as st
import pandas as pd

# --- Sheet parameters DataFrame ---
sheet_params = pd.DataFrame({
    'SheetName': ['Equities', 'FEXD', 'Bonds', 'FX', 'Energy', 'Metals', 'Crops', 'Softs'],
    'Hedge_skiprows': [1, 1, 1, 1, 1, 1, 1, 1],
    'Hedge_nrows': [17, 8, 19, 9, 9, 6, 9, 10],
    'Price_skiprows': [20, 11, 23, 12, 12, 8, 12, 12],
    'Price_nrows': [17, 8, 19, 9, 9, 6, 9, 10],
    'LastProduct': ['SXF', 'FEXD24', 'BAX', 'UKNG', 'UKNG', 'COPPER', 'RICE', 'LUMBER']
})

file_path = "Spread Ratios.xlsx"
excel_data = pd.ExcelFile(file_path)

def get_sheet_params(sheet_name):
    row = sheet_params[sheet_params['SheetName'] == sheet_name]
    if row.empty:
        st.error(f"Sheet name '{sheet_name}' not found in parameters.")
        st.stop()
    return row.iloc[0]

def clean_columns(df):
    return df.loc[:, [col for col in df.columns if not str(col).startswith("Unnamed") and str(col).strip() != ""]]

def clean_rows(df):
    if 'Product' in df.columns:
        df = df[df['Product'].notna()]
        df = df[~df['Product'].astype(str).str.startswith("Unnamed")]
        df = df[df['Product'].astype(str).str.strip() != ""]
    return df

def get_product_list(sheet_name):
    params = get_sheet_params(sheet_name)
    hedge_df = excel_data.parse(
        sheet_name=sheet_name,
        skiprows=int(params['Hedge_skiprows']),
        nrows=int(params['Hedge_nrows']),
        header=0
    )
    hedge_df = clean_columns(hedge_df)
    hedge_df = clean_rows(hedge_df)
    products = [col for col in hedge_df.columns if col != 'Product']
    if 'Product' in hedge_df.columns:
        products += hedge_df['Product'].dropna().unique().tolist()
    products = sorted(set([str(p).strip() for p in products if pd.notna(p) and str(p).strip() != ""]))
    return products

def get_ratios(product1, product2, sheet_name):
    params = get_sheet_params(sheet_name)
    hedge_df = excel_data.parse(
        sheet_name=sheet_name,
        skiprows=int(params['Hedge_skiprows']),
        nrows=int(params['Hedge_nrows']),
        header=0
    )
    price_df = excel_data.parse(
        sheet_name=sheet_name,
        skiprows=int(params['Price_skiprows']),
        nrows=int(params['Price_nrows']),
        header=0
    )
    hedge_df = clean_columns(hedge_df)
    price_df = clean_columns(price_df)
    hedge_df = clean_rows(hedge_df)
    price_df = clean_rows(price_df)
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

def round_ratio(val, decimals=1):
    try:
        if isinstance(val, (int, float)) and not pd.isna(val):
            return round(val, decimals)
        return val
    except Exception:
        return val

# --- Streamlit UI ---
st.title("Spread Ratio Dashboard")

sheet_name = st.selectbox("Select your sheet (product type):", sheet_params['SheetName'].tolist())

if sheet_name:
    products = get_product_list(sheet_name)
    product1 = st.selectbox("Select Product 1:", products, key="prod1")
    product2 = st.selectbox("Select Product 2:", products, key="prod2")

    if product1 and product2 and product1 != product2:
        hedge_ratio, price_ratio = get_ratios(product1, product2, sheet_name)
        hedge_ratio_rounded = round_ratio(hedge_ratio, 1)
        price_ratio_rounded = round_ratio(price_ratio, 1)
        st.markdown(f"### Results for **{product1}** and **{product2}** in **{sheet_name}**")
        st.write(f"**Hedge Ratio:** {hedge_ratio_rounded}")
        st.write(f"**Price Ratio:** {price_ratio_rounded}")
    elif product1 == product2:
        st.info("Please select two different products.")
