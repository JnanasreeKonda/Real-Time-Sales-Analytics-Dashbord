import streamlit as st
import pandas as pd
import altair as alt
import time
from engine.processor import preprocess_incoming_row

# Page Setup
st.set_page_config(page_title="Global Sales Analytics", layout="wide")
st.title("🌍 Real-Time Sales Analytics Dashboard")
st.markdown("Real-time analytics from start to current time")

# Session State
if 'buffer' not in st.session_state:
    st.session_state.buffer = pd.DataFrame()
if 'count' not in st.session_state:
    st.session_state.count = 0

# Sidebar Controls
st.sidebar.header("Dashboard Controls")
sim_speed = st.sidebar.select_slider(
    "Stream Speed (seconds per update)",
    options=[1.0, 0.8, 0.5, 0.3],
    value=0.5
)

if st.sidebar.button("Reset Global Stream"):
    st.session_state.count = 0
    st.session_state.buffer = pd.DataFrame()
    st.rerun()

# Load Data
@st.cache_data
def get_data():
    df = pd.read_excel('data/online_retail.xlsx')
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    return df

source_df = get_data()

# Layout Placeholders
kpi_placeholder = st.empty()

st.subheader("Revenue by Country (%)")
pie_placeholder = st.empty()

st.subheader("Orders per Country")
orders_placeholder = st.empty()

st.subheader("Unique Customers per Country")
customers_placeholder = st.empty()

st.subheader("Top 5 Products by Units Sold")
bar_units_placeholder = st.empty()

st.subheader("Top 5 Products by Revenue")
bar_revenue_placeholder = st.empty()

st.subheader("Revenue Over Time")
cum_line_placeholder = st.empty()

st.subheader("Revenue Table by Country")
table_placeholder = st.empty()

UPDATE_EVERY = 5

for i in range(st.session_state.count, len(source_df)):
    raw_row = source_df.iloc[[i]].copy()
    clean_row = preprocess_incoming_row(raw_row)

    if clean_row is not None:
        st.session_state.buffer = pd.concat([st.session_state.buffer, clean_row])

    if i % UPDATE_EVERY == 0 and not st.session_state.buffer.empty:
        df = st.session_state.buffer.copy()

        # Rename columns for clarity
        df = df.rename(columns={
            'Description': 'Product',
            'Quantity': 'Units Sold',
            'TotalRevenue': 'Revenue',
            'Country': 'Country',
            'UniqueCustomers': 'Unique_Customers',
        })

        # KPIs
        total_revenue = df['Revenue'].sum()
        total_units = int(df['Units Sold'].sum())
        total_orders = len(df)
        active_countries = df['Country'].nunique()
        unique_customers = df['CustomerID'].nunique() if 'CustomerID' in df.columns else 0
        aov = total_revenue / max(total_orders, 1)

        with kpi_placeholder.container():
            c1, c2, c3, c4, c5, c6 = st.columns(6)
            c1.metric("Revenue", f"${total_revenue:,.2f}")
            c2.metric("Units Sold", total_units)
            c3.metric("Orders", total_orders)
            c4.metric("Active Countries", active_countries)
            c5.metric("Unique Customers", unique_customers)
            c6.metric("Average Order Value", f"${aov:,.2f}")

        # Revenue by Country Pie Chart
        country_stats = df.groupby("Country").agg(
            Revenue=('Revenue', 'sum'),
            Orders=('Product', 'count'),
            Unique_Customers=('CustomerID', pd.Series.nunique if 'CustomerID' in df.columns else lambda x: 0)
        ).reset_index()
        country_stats['Percentage of Revenue'] = country_stats['Revenue'] / country_stats['Revenue'].sum() * 100

        pie_chart = alt.Chart(country_stats).mark_arc(innerRadius=40).encode(
            theta='Revenue:Q',
            color=alt.Color('Country:N', scale=alt.Scale(scheme='pastel1'), legend=alt.Legend(title="Country")),
            tooltip=[
                alt.Tooltip('Country:N'),
                alt.Tooltip('Revenue:Q', title='Revenue ($)', format=',.2f'),
                alt.Tooltip('Percentage of Revenue:Q', title='% Revenue', format=".1f")
            ]
        )
        pie_placeholder.altair_chart(pie_chart, use_container_width=True)

        # Top 5 Products by Units Sold
        top_units = df.groupby("Product")['Units Sold'].sum().reset_index().sort_values('Units Sold', ascending=False).head(5)
        bar_units = alt.Chart(top_units).mark_bar().encode(
            x='Units Sold:Q',
            y=alt.Y('Product:N', sort='-x'),
            tooltip=['Product', 'Units Sold'],
            color=alt.Color('Units Sold:Q', scale=alt.Scale(scheme='viridis'))
        ).properties(height=250)
        bar_units_placeholder.altair_chart(bar_units, use_container_width=True)

        # Top 5 Products by Revenue
        top_revenue = df.groupby("Product")['Revenue'].sum().reset_index().sort_values('Revenue', ascending=False).head(5)
        bar_revenue = alt.Chart(top_revenue).mark_bar().encode(
            x='Revenue:Q',
            y=alt.Y('Product:N', sort='-x'),
            tooltip=['Product', alt.Tooltip('Revenue', title='Revenue ($)', format=',.2f')],
            color=alt.Color('Revenue:Q', scale=alt.Scale(scheme='magma'))
        ).properties(height=250)
        bar_revenue_placeholder.altair_chart(bar_revenue, use_container_width=True)

        # Revenue Over Time Line Chart
        df_sorted = df.sort_values('InvoiceDate')
        df_sorted['CumulativeRevenue'] = df_sorted['Revenue'].cumsum()
        cum_line = alt.Chart(df_sorted).mark_line(color='green').encode(
            x='InvoiceDate:T',
            y='CumulativeRevenue:Q',
            tooltip=[alt.Tooltip('InvoiceDate:T', title='Time'),
                     alt.Tooltip('CumulativeRevenue:Q', title='Revenue ($)', format=',.2f')]
        ).properties(height=250)
        cum_line_placeholder.altair_chart(cum_line, use_container_width=True)

        # Orders per Country Bubble Chart
        bubble_chart = alt.Chart(country_stats).mark_circle(opacity=0.8).encode(
            x=alt.X('Country:N', sort='-y', title="Country"),
            y=alt.Y('Orders:Q', title="Number of Orders"),
            size=alt.Size('Orders:Q', scale=alt.Scale(range=[100, 1000]), legend=None),
            color=alt.Color('Country:N', legend=alt.Legend(title="Country")),
            tooltip=['Country', 'Orders']
        ).properties(height=250)

        orders_placeholder.altair_chart(bubble_chart, use_container_width=True)

        # Unique Customers per Country Heatmap
        heatmap = alt.Chart(country_stats).mark_rect().encode(
            x='Country:N',
            y='Unique_Customers:Q',
            color=alt.Color('Country:N', legend=alt.Legend(title="Country")),
            tooltip=['Country', 'Unique_Customers']
        ).properties(height=250)

        customers_placeholder.altair_chart(heatmap, use_container_width=True)

        # Revenue Table by Country (with Orders & Unique Customers)
        table_placeholder.dataframe(
            country_stats.sort_values('Revenue', ascending=False),
            use_container_width=True
        )

    time.sleep(sim_speed)
    st.session_state.count += 1



