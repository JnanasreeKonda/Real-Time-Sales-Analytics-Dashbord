import streamlit as st
import pandas as pd
import altair as alt
import time
from engine.calculations import get_live_metrics
from engine.processor import preprocess_incoming_row

st.set_page_config(page_title="Global Sales Analytics", layout="wide")

st.title("🌍 Real-Time Global Sales Analytics")
st.markdown("Designed for **Internal Data Tooling & Research Analytics**")

# --- Session State ---
if 'buffer' not in st.session_state:
    st.session_state.buffer = pd.DataFrame()
if 'count' not in st.session_state:
    st.session_state.count = 0

# --- Sidebar ---
st.sidebar.header("Dashboard Controls")
sim_speed = st.sidebar.select_slider(
    "Stream Speed",
    options=[1.0, 0.8, 0.5, 0.3],
    value=0.5
)

if st.sidebar.button("Reset Global Stream"):
    st.session_state.count = 0
    st.session_state.buffer = pd.DataFrame()
    st.rerun()

# --- Data ---
@st.cache_data
def get_data():
    return pd.read_excel('data/online_retail.xlsx')

source_df = get_data()

# --- UI Placeholders ---
kpi_row = st.empty()
pie_placeholder = st.empty()
bar_placeholder = st.empty()
table_placeholder = st.empty()

UPDATE_EVERY = 5  # batch updates

# --- Stream Loop ---
for i in range(st.session_state.count, len(source_df)):
    raw_row = source_df.iloc[[i]].copy()
    clean_row = preprocess_incoming_row(raw_row)

    if clean_row is not None:
        st.session_state.buffer = pd.concat(
            [st.session_state.buffer, clean_row]
        ).tail(200)

    # Update only every N rows
    if i % UPDATE_EVERY == 0 and not st.session_state.buffer.empty:
        df = st.session_state.buffer
        country_stats, top_items = get_live_metrics(df)

        # --- KPIs ---
        with kpi_row.container():
            c1, c2, c3 = st.columns(3)
            c1.metric("Revenue (Window)", f"${df['TotalRevenue'].sum():,.2f}")
            c2.metric("Active Countries", df['Country'].nunique())
            c3.metric("Units Sold", int(df['Quantity'].sum()))

        # --- Pie Chart ---
        pie = alt.Chart(country_stats).mark_arc(innerRadius=40).encode(
            theta="TotalRevenue:Q",
            color=alt.Color("Country:N", legend=None),
            tooltip=["Country", "TotalRevenue"]
        ).properties(height=250)

        pie_placeholder.altair_chart(pie, use_container_width=True)

        # --- Bar Chart ---
        bar = alt.Chart(top_items).mark_bar().encode(
            x="Quantity:Q",
            y=alt.Y("Description:N", sort='-x'),
            tooltip=["Description", "Quantity"]
        ).properties(height=250)

        bar_placeholder.altair_chart(bar, use_container_width=True)

        # --- Table ---
        with table_placeholder:
            st.dataframe(
                country_stats.sort_values(
                    by='TotalRevenue',
                    ascending=False
                ),
                use_container_width=True
            )

    time.sleep(sim_speed)
    st.session_state.count += 1


