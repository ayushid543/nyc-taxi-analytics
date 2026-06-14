import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page Config ───────────────────────────────────────────
st.set_page_config(
    page_title="NYC Taxi Analytics",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {background-color: #f8fafc; border-bottom: 1px solid #e2e8f0;}
    .stDeployButton {display: none;}
    [data-testid="stToolbar"] {display: none;}

    .kpi-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .kpi-label {
        color: #64748b;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 8px;
    }
    .kpi-value {
        color: #0f172a;
        font-size: 26px;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    .kpi-delta {
        color: #10b981;
        font-size: 12px;
        margin-top: 4px;
    }

    .section-header {
        color: #0f172a;
        font-size: 16px;
        font-weight: 600;
        margin: 20px 0 10px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# ── Chart theme ───────────────────────────────────────────
CHART_BG = "#ffffff"
GRID = "#f1f5f9"
FONT = "#374151"

def style_fig(fig):
    fig.update_layout(
        paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,
        font=dict(color=FONT, family="Inter, sans-serif", size=12),
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(bgcolor=CHART_BG, bordercolor="#e2e8f0", borderwidth=1),
    )
    fig.update_xaxes(gridcolor=GRID, linecolor="#e2e8f0", zeroline=False)
    fig.update_yaxes(gridcolor=GRID, linecolor="#e2e8f0", zeroline=False)
    return fig

# ── Data Loading ──────────────────────────────────────────
@st.cache_data
def load_data():
    conn = duckdb.connect("dbt_project/dev.duckdb", read_only=True)
    hourly = conn.execute("SELECT * FROM main.mart_hourly_trips ORDER BY hour_of_day").df()
    payment = conn.execute("SELECT * FROM main.mart_payment_summary").df()
    duration = conn.execute("""
        SELECT 
            hour(pickup_datetime) as hour_of_day,
            dayofweek(pickup_datetime) as day_of_week,
            avg(trip_duration_minutes) as avg_duration,
            avg(trip_distance) as avg_distance,
            count(*) as trips
        FROM main.stg_taxi_trips
        GROUP BY 1, 2
        ORDER BY 1
    """).df()
    conn.close()
    return hourly, payment, duration

hourly, payment, duration = load_data()

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🚕 NYC Taxi Analytics")
    st.markdown("**January 2024**")
    st.divider()

    st.markdown("#### Filters")
    day_map = {0: "Sun", 1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat"}
    selected_days = st.multiselect(
        "Day of Week",
        options=list(day_map.keys()),
        default=list(day_map.keys()),
        format_func=lambda x: day_map[x]
    )
    hour_range = st.slider("Hour of Day", 0, 23, (0, 23))

    st.divider()
    st.markdown("#### Stack")
    st.markdown("- 🦆 **DuckDB** — OLAP engine\n- 🔧 **dbt Core** — transformations\n- 📊 **Streamlit** — dashboard")
    st.divider()
    st.markdown("Built by **Ayushi Desai**")
    st.markdown("[GitHub](https://github.com/ayushid543) · [LinkedIn](https://linkedin.com/in/ayushi-desai)")

# ── Filters ───────────────────────────────────────────────
filtered_hourly = hourly[
    (hourly["day_of_week"].isin(selected_days)) &
    (hourly["hour_of_day"].between(hour_range[0], hour_range[1]))
]
filtered_duration = duration[
    (duration["day_of_week"].isin(selected_days)) &
    (duration["hour_of_day"].between(hour_range[0], hour_range[1]))
]

# ── Header ────────────────────────────────────────────────
st.markdown("# 🚕 NYC Taxi Analytics — January 2024")
st.markdown("*2.7M trips · $74.6M revenue · Built with dbt + DuckDB + Streamlit*")
st.divider()

# ── KPIs ─────────────────────────────────────────────────
total_trips = filtered_hourly["total_trips"].sum()
total_revenue = filtered_hourly["total_revenue"].sum()
avg_fare = filtered_hourly["avg_fare"].mean()
avg_tip = filtered_hourly["avg_tip"].mean()
avg_duration = filtered_duration["avg_duration"].mean()

k1, k2, k3, k4, k5 = st.columns(5)
for col, label, value, delta in [
    (k1, "Total Trips", f"{total_trips:,.0f}", "2.7M records analyzed"),
    (k2, "Total Revenue", f"${total_revenue:,.0f}", "January 2024"),
    (k3, "Avg Fare", f"${avg_fare:.2f}", "Per trip"),
    (k4, "Avg Tip", f"${avg_tip:.2f}", "Per trip"),
    (k5, "Avg Duration", f"{avg_duration:.1f} min", "Per trip"),
]:
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-delta">{delta}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["Demand & Revenue", "Trip Analysis", "Data Table"])

# ── TAB 1 ─────────────────────────────────────────────────
with tab1:
    by_hour = filtered_hourly.groupby("hour_of_day").agg(
        total_trips=("total_trips", "sum"),
        avg_fare=("avg_fare", "mean"),
        total_revenue=("total_revenue", "sum")
    ).reset_index()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Trips by Hour of Day</div>', unsafe_allow_html=True)
        fig1 = px.bar(
            by_hour, x="hour_of_day", y="total_trips",
            color="total_trips",
            color_continuous_scale=[[0, "#bfdbfe"], [0.5, "#3b82f6"], [1, "#1d4ed8"]],
            labels={"hour_of_day": "Hour", "total_trips": "Total Trips"},
            custom_data=["avg_fare"]
        )
        fig1.update_traces(hovertemplate="<b>%{x}:00</b><br>Trips: %{y:,.0f}<br>Avg Fare: $%{customdata[0]:.2f}<extra></extra>")
        fig1.update_coloraxes(showscale=False)
        st.plotly_chart(style_fig(fig1), use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Revenue vs Avg Fare by Hour</div>', unsafe_allow_html=True)
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])
        fig2.add_trace(go.Bar(
            x=by_hour["hour_of_day"], y=by_hour["total_revenue"],
            name="Total Revenue", marker_color="#93c5fd", opacity=0.85,
            hovertemplate="Hour %{x}: $%{y:,.0f}<extra></extra>"
        ), secondary_y=False)
        fig2.add_trace(go.Scatter(
            x=by_hour["hour_of_day"], y=by_hour["avg_fare"],
            name="Avg Fare", line=dict(color="#f59e0b", width=2.5),
            mode="lines+markers", marker=dict(size=5),
            hovertemplate="Avg Fare: $%{y:.2f}<extra></extra>"
        ), secondary_y=True)
        fig2.update_yaxes(title_text="Total Revenue ($)", secondary_y=False, gridcolor=GRID, color=FONT)
        fig2.update_yaxes(title_text="Avg Fare ($)", secondary_y=True, color="#f59e0b")
        fig2.update_xaxes(title_text="Hour of Day", gridcolor=GRID, color=FONT)
        st.plotly_chart(style_fig(fig2), use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="section-header">Trips by Day of Week</div>', unsafe_allow_html=True)
        dow = filtered_hourly.groupby("day_of_week")["total_trips"].sum().reset_index()
        dow["day_name"] = dow["day_of_week"].map(day_map)
        dow = dow.sort_values("day_of_week")
        fig3 = px.bar(
            dow, x="day_name", y="total_trips",
            color="total_trips",
            color_continuous_scale=[[0, "#ddd6fe"], [0.5, "#7c3aed"], [1, "#4c1d95"]],
            labels={"day_name": "Day", "total_trips": "Total Trips"},
        )
        fig3.update_coloraxes(showscale=False)
        fig3.update_traces(hovertemplate="<b>%{x}</b><br>Trips: %{y:,.0f}<extra></extra>")
        st.plotly_chart(style_fig(fig3), use_container_width=True)

    with col4:
        st.markdown('<div class="section-header">Revenue by Payment Type</div>', unsafe_allow_html=True)
        fig4 = px.pie(
            payment, values="total_revenue", names="payment_type_name",
            color_discrete_sequence=["#1d4ed8", "#3b82f6", "#93c5fd", "#bfdbfe", "#dbeafe"],
            hole=0.5
        )
        fig4.update_traces(
            textposition="outside",
            hovertemplate="<b>%{label}</b><br>Revenue: $%{value:,.0f}<br>Share: %{percent}<extra></extra>"
        )
        fig4.update_layout(paper_bgcolor=CHART_BG, font=dict(color=FONT),
                           margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig4, use_container_width=True)

# ── TAB 2 ─────────────────────────────────────────────────
with tab2:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Avg Trip Duration & Distance by Hour</div>', unsafe_allow_html=True)
        dur_by_hour = filtered_duration.groupby("hour_of_day").agg(
            avg_duration=("avg_duration", "mean"),
            avg_distance=("avg_distance", "mean")
        ).reset_index()

        fig5 = make_subplots(specs=[[{"secondary_y": True}]])
        fig5.add_trace(go.Scatter(
            x=dur_by_hour["hour_of_day"], y=dur_by_hour["avg_duration"],
            name="Avg Duration (min)", line=dict(color="#10b981", width=2.5),
            fill="tozeroy", fillcolor="rgba(16,185,129,0.08)",
            hovertemplate="Hour %{x}: %{y:.1f} min<extra></extra>"
        ), secondary_y=False)
        fig5.add_trace(go.Scatter(
            x=dur_by_hour["hour_of_day"], y=dur_by_hour["avg_distance"],
            name="Avg Distance (mi)", line=dict(color="#f59e0b", width=2, dash="dot"),
            hovertemplate="Avg Distance: %{y:.2f} mi<extra></extra>"
        ), secondary_y=True)
        fig5.update_yaxes(title_text="Duration (minutes)", secondary_y=False, gridcolor=GRID, color="#10b981")
        fig5.update_yaxes(title_text="Distance (miles)", secondary_y=True, color="#f59e0b")
        fig5.update_xaxes(title_text="Hour of Day", gridcolor=GRID, color=FONT)
        st.plotly_chart(style_fig(fig5), use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Avg Tip by Payment Type</div>', unsafe_allow_html=True)
        fig6 = go.Figure()
        fig6.add_trace(go.Bar(
            x=payment["payment_type_name"],
            y=payment["avg_tip"],
            marker=dict(color=payment["avg_tip"],
                        colorscale=[[0, "#d1fae5"], [0.5, "#10b981"], [1, "#065f46"]]),
            text=payment["avg_tip"].apply(lambda x: f"${x:.2f}"),
            textposition="outside",
            textfont=dict(color=FONT),
            hovertemplate="<b>%{x}</b><br>Avg Tip: $%{y:.2f}<extra></extra>"
        ))
        fig6.update_layout(xaxis_title="Payment Type", yaxis_title="Avg Tip ($)", showlegend=False)
        st.plotly_chart(style_fig(fig6), use_container_width=True)

    st.markdown('<div class="section-header">Trip Volume Heatmap — Hour x Day of Week</div>', unsafe_allow_html=True)
    heat_data = filtered_hourly.pivot_table(
        index="day_of_week", columns="hour_of_day",
        values="total_trips", aggfunc="sum"
    ).fillna(0)
    heat_data.index = [day_map.get(i, i) for i in heat_data.index]

    fig7 = px.imshow(
        heat_data,
        color_continuous_scale=[[0, "#eff6ff"], [0.4, "#93c5fd"], [0.7, "#3b82f6"], [1, "#1e3a8a"]],
        labels=dict(x="Hour of Day", y="Day of Week", color="Trips"),
        aspect="auto"
    )
    fig7.update_traces(hovertemplate="<b>%{y} at %{x}:00</b><br>Trips: %{z:,.0f}<extra></extra>")
    fig7.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
                       font=dict(color=FONT), margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig7, use_container_width=True)

# ── TAB 3 ─────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-header">Hourly Stats Summary</div>', unsafe_allow_html=True)

    display_df = filtered_hourly.groupby("hour_of_day").agg(
        total_trips=("total_trips", "sum"),
        total_revenue=("total_revenue", "sum"),
        avg_fare=("avg_fare", "mean"),
        avg_tip=("avg_tip", "mean"),
        avg_distance=("avg_distance_miles", "mean"),
        tip_pct=("tip_pct", "mean")
    ).reset_index()

    display_df.columns = ["Hour", "Total Trips", "Total Revenue ($)",
                           "Avg Fare ($)", "Avg Tip ($)", "Avg Distance (mi)", "Tip %"]
    display_df["Total Trips"] = display_df["Total Trips"].apply(lambda x: f"{x:,.0f}")
    display_df["Total Revenue ($)"] = display_df["Total Revenue ($)"].apply(lambda x: f"${x:,.0f}")
    display_df["Avg Fare ($)"] = display_df["Avg Fare ($)"].apply(lambda x: f"${x:.2f}")
    display_df["Avg Tip ($)"] = display_df["Avg Tip ($)"].apply(lambda x: f"${x:.2f}")
    display_df["Avg Distance (mi)"] = display_df["Avg Distance (mi)"].apply(lambda x: f"{x:.2f}")
    display_df["Tip %"] = display_df["Tip %"].apply(lambda x: f"{x:.1f}%")

    st.dataframe(display_df, use_container_width=True, hide_index=True, height=500)

    st.divider()
    st.markdown('<div class="section-header">Payment Type Breakdown</div>', unsafe_allow_html=True)

    pay_display = payment.copy()
    pay_display.columns = ["Payment Type", "Total Trips", "Total Revenue ($)", "Avg Tip ($)", "Avg Fare ($)"]
    pay_display["Total Trips"] = pay_display["Total Trips"].apply(lambda x: f"{x:,.0f}")
    pay_display["Total Revenue ($)"] = pay_display["Total Revenue ($)"].apply(lambda x: f"${x:,.0f}")
    pay_display["Avg Tip ($)"] = pay_display["Avg Tip ($)"].apply(lambda x: f"${x:.2f}")
    pay_display["Avg Fare ($)"] = pay_display["Avg Fare ($)"].apply(lambda x: f"${x:.2f}")
    st.dataframe(pay_display, use_container_width=True, hide_index=True)
