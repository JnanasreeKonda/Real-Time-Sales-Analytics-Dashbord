import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time
from engine.calculations import get_live_metrics
from engine.processor import preprocess_incoming_row

st.set_page_config(page_title="Global Sales Analytics", layout="wide")

# --- UI Setup ---
st.title("🌍 Real-Time Global Sales Analytics")
st.markdown("Designed for **Internal Data Tooling** & **Research Analytics**")

if 'buffer' not in st.session_state:
    st.session_state.buffer = pd.DataFrame()
if 'count' not in st.session_state:
    st.session_state.count = 0

# --- Sidebar Controls (BEFORE THE LOOP) ---
st.sidebar.header("Dashboard Controls")
sim_speed = st.sidebar.select_slider("Stream Speed", options=[1.0, 0.5, 0.1, 0.01], value=0.5)

if st.sidebar.button("Reset Global Stream", key="reset"):
    st.session_state.count = 0
    st.session_state.buffer = pd.DataFrame()
    st.rerun()


# --- Data Source ---
@st.cache_data
def get_data():
    return pd.read_excel('data/online_retail.xlsx')


source_df = get_data()

# --- Main Dashboard Placeholders ---
metric_cols = st.columns(3)
chart_col1, chart_col2 = st.columns(2)
table_place = st.empty()

# --- The Stream ---
for i in range(st.session_state.count, len(source_df)):
    raw_row = source_df.iloc[[i]].copy()
    clean_row = preprocess_incoming_row(raw_row)

    if clean_row is not None:
        # Buffer keeps a rolling window of the last 150 transactions
        st.session_state.buffer = pd.concat([st.session_state.buffer, clean_row]).tail(150)

    if not st.session_state.buffer.empty:
        df = st.session_state.buffer
        country_stats, top_items = get_live_metrics(df)

        # 1. Update KPIs
        metric_cols[0].metric("Total Revenue (Window)", f"${df['TotalRevenue'].sum():,.2f}")
        metric_cols[1].metric("Active Countries", df['Country'].nunique())
        metric_cols[2].metric("Total Units Sold", int(df['Quantity'].sum()))

        # 2. Revenue Pie Chart
        with chart_col1:
            st.write("### Revenue Mix by Country")
            fig1, ax1 = plt.subplots(figsize=(5, 4))
            ax1.pie(country_stats['TotalRevenue'], labels=country_stats['Country'],
                    autopct='%1.1f%%', colors=sns.color_palette('pastel'))
            st.pyplot(fig1, clear_figure=True)

        # 3. Top Items Bar Chart
        with chart_col2:
            st.write("### Top 5 Products by Volume")
            fig2, ax2 = plt.subplots(figsize=(5, 4))
            sns.barplot(data=top_items, x='Quantity', y='Description', palette='viridis', ax=ax2)
            st.pyplot(fig2, clear_figure=True)

        # 4. Data Table
        with table_place.container():
            st.write("### Live Geographic Breakdown")
            st.dataframe(country_stats.sort_values(by='TotalRevenue', ascending=False), use_container_width=True)

    time.sleep(sim_speed)
    st.session_state.count += 1