import numpy as np

def calculate_eoq(annual_demand, order_cost, holding_cost):
    """Economic Order Quantity - Standard Optimization Model."""
    if holding_cost <= 0 or annual_demand <= 0:
        return 0
    return np.sqrt((2 * annual_demand * order_cost) / holding_cost)

def calculate_reorder_point(avg_daily_demand, lead_time_days, safety_stock):
    """Calculates when to restock based on lead time and buffers."""
    return (avg_daily_demand * lead_time_days) + safety_stock

def get_realtime_forecast(series, window=10):
    """
    Predicts next-step demand using EWMA.
    """
    if len(series) < 2:
        return 0
    return series.ewm(span=window).mean().iloc[-1]

def get_live_metrics(df):
    """
    Groups data for real-time visualization.
    """
    # Revenue and Unique Customers by Country
    country_stats = df.groupby('Country').agg({
        'TotalRevenue': 'sum',
        'CustomerID': 'nunique'
    }).rename(columns={'CustomerID': 'Unique_Customers'}).reset_index()

    # Top 5 items by total quantity sold
    top_items = df.groupby('Description')['Quantity'].sum().nlargest(5).reset_index()

    return country_stats, top_items