import pandas as pd


def preprocess_incoming_row(row_df):
    """
    Validates and standardizes incoming data.
    Now strictly filters out invalid country data.
    """
    try:
        # Null Check for IDs and Country
        if row_df['CustomerID'].isnull().values.any() or row_df['Country'].isnull().values.any():
            return None

        # String Normalization
        country_raw = str(row_df['Country'].iloc[0]).strip()

        # Filter out "Unspecified" or empty country strings
        if country_raw.lower() in ['unspecified', 'nan', 'none', '']:
            return None

        # Standardize for the Pie Chart slice label
        row_df['Country'] = country_raw.title()
        row_df['Description'] = str(row_df['Description'].iloc[0]).strip().upper()

        # Numeric Enforcement & Bounds Check
        row_df['Quantity'] = pd.to_numeric(row_df['Quantity'], errors='coerce')
        row_df['UnitPrice'] = pd.to_numeric(row_df['UnitPrice'], errors='coerce')

        if (row_df['Quantity'].iloc[0] <= 0) or (row_df['UnitPrice'].iloc[0] <= 0):
            return None

        # Feature Engineering
        row_df['TotalRevenue'] = row_df['Quantity'] * row_df['UnitPrice']

        return row_df

    except Exception as e:
        return None