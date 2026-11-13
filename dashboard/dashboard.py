import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.set_page_config(
    page_title="Bike Sharing Analytics Dashboard",
    page_icon="🚲",
    layout="wide"
)

sns.set_theme(style="whitegrid")
plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.right"] = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_data
def load_data():
    day_df = pd.read_csv(os.path.join(BASE_DIR, "main_data.csv"))
    hour_df = pd.read_csv(os.path.join(BASE_DIR, "hour_data.csv"))
    day_df["dteday"] = pd.to_datetime(day_df["dteday"])
    hour_df["dteday"] = pd.to_datetime(hour_df["dteday"])
    return day_df, hour_df

day_df, hour_df = load_data()

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filter Data")
min_date = day_df["dteday"].min().date()
max_date = day_df["dteday"].max().date()

date_range = st.sidebar.date_input(
    "Rentang Tanggal",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

selected_seasons = st.sidebar.multiselect(
    "Musim (Season)",
    options=["Spring", "Summer", "Fall", "Winter"],
    default=["Spring", "Summer", "Fall", "Winter"]
)

selected_day_types = st.sidebar.multiselect(
    "Tipe Hari",
    options=["Working Day", "Weekend / Holiday"],
    default=["Working Day", "Weekend / Holiday"]
)

selected_weather = st.sidebar.multiselect(
    "Kondisi Cuaca",
    options=["Clear / Partly Cloudy", "Mist / Cloudy", "Light Snow / Rain", "Heavy Rain / Ice"],
    default=["Clear / Partly Cloudy", "Mist / Cloudy", "Light Snow / Rain", "Heavy Rain / Ice"]
)

# Filter datasets
day_filtered = day_df[
    (day_df["dteday"].dt.date >= start_date) &
    (day_df["dteday"].dt.date <= end_date) &
    (day_df["season_label"].isin(selected_seasons)) &
    (day_df["day_type"].isin(selected_day_types)) &
    (day_df["weather_label"].isin(selected_weather))
]

hour_filtered = hour_df[
    (hour_df["dteday"].dt.date >= start_date) &
    (hour_df["dteday"].dt.date <= end_date) &
    (hour_df["season_label"].isin(selected_seasons)) &
    (hour_df["day_type"].isin(selected_day_types)) &
    (hour_df["weather_label"].isin(selected_weather))
]

# --- HEADER & KPI ---
st.title("🚲 Bike Sharing Analytics Dashboard (2011–2012)")
st.markdown(
    "Dashboard interaktif ini menyajikan hasil analisis pola penyewaan sepeda, "
    "perbandingan segmen pengguna (**Casual vs Registered**), pengaruh cuaca, serta klasterisasi waktu operasional."
)

if day_filtered.empty or hour_filtered.empty:
    st.warning("Tidak ada data yang sesuai dengan kombinasi filter yang dipilih. Silakan ubah filter di sidebar.")
    st.stop()

total_rentals = int(day_filtered["cnt"].sum())
total_reg = int(day_filtered["registered"].sum())
total_cas = int(day_filtered["casual"].sum())
avg_daily = day_filtered["cnt"].mean()
reg_pct = (total_reg / total_rentals * 100) if total_rentals > 0 else 0
cas_pct = (total_cas / total_rentals * 100) if total_rentals > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Penyewaan", f"{total_rentals:,}")
col2.metric("Registered Users", f"{total_reg:,}", f"{reg_pct:.1f}% dari total")
col3.metric("Casual Users", f"{total_cas:,}", f"{cas_pct:.1f}% dari total")
col4.metric("Rata-rata Harian", f"{avg_daily:,.1f} / hari")

st.divider()

# --- SECTION 1: MUSIM & TREN BULANAN ---
st.subheader("1. Perbandingan Musiman & Tren Pertumbuhan Bulanan")
c1, c2 = st.columns(2)

with c1:
    season_order = [s for s in ["Spring", "Summer", "Fall", "Winter"] if s in day_filtered["season_label"].unique()]
    season_plot = day_filtered.groupby("season_label")[["registered", "casual"]].mean().reindex(season_order)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    x = np.arange(len(season_order))
    ax.bar(x, season_plot["registered"], width=0.55, label="Registered", color="#1f77b4")
    ax.bar(x, season_plot["casual"], width=0.55, bottom=season_plot["registered"], label="Casual", color="#ff7f0e")
    for i, (r, c) in enumerate(zip(season_plot["registered"], season_plot["casual"])):
        ax.text(i, r + c + 100, f"{r + c:,.0f}", ha="center", va="bottom", fontweight="bold", fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels(season_order)
    ax.set_ylabel("Rata-rata Penyewaan / Hari")
    ax.set_title("Rata-rata Penyewaan Harian per Musim")
    ax.set_ylim(0, max((season_plot["registered"] + season_plot["casual"]).max() * 1.15, 100))
    ax.legend(frameon=False)
    st.pyplot(fig)
    plt.close(fig)

with c2:
    monthly_yoy = day_filtered.groupby(["year_label", "mnth"])["cnt"].mean().unstack(level=0)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    if 2011 in monthly_yoy.columns:
        ax.plot(monthly_yoy.index, monthly_yoy[2011], marker="o", linewidth=2.2, color="#7f7f7f", label="2011")
    if 2012 in monthly_yoy.columns:
        ax.plot(monthly_yoy.index, monthly_yoy[2012], marker="o", linewidth=2.6, color="#1f77b4", label="2012")
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(month_names)
    ax.set_ylabel("Rata-rata Penyewaan / Hari")
    ax.set_title("Tren Bulanan: 2011 vs 2012")
    ax.set_ylim(0, max(monthly_yoy.max().max() * 1.15, 100))
    ax.legend(frameon=False)
    st.pyplot(fig)
    plt.close(fig)

# --- SECTION 2: POLA JAM OPERASIONAL ---
st.subheader("2. Pola Jam Operasional: Working Day vs Weekend / Holiday")
fig, ax = plt.subplots(figsize=(12, 4.5))
for dtype, color, ls in [("Working Day", "#1f77b4", "-"), ("Weekend / Holiday", "#ff7f0e", "--")]:
    sub = hour_filtered[hour_filtered["day_type"] == dtype].groupby("hr")["cnt"].mean()
    if not sub.empty:
        ax.plot(sub.index, sub.values, marker="o", markersize=4, linewidth=2.4, linestyle=ls, color=color, label=dtype)
ax.set_xticks(range(0, 24))
ax.set_xlabel("Jam (00:00 – 23:00)")
ax.set_ylabel("Rata-rata Penyewaan / Jam")
ax.set_title("Rata-rata Penyewaan per Jam Berdasarkan Tipe Hari")
ax.set_ylim(0, max(hour_filtered.groupby(["day_type", "hr"])["cnt"].mean().max() * 1.15, 50))
ax.legend(frameon=False)
st.pyplot(fig)
plt.close(fig)

# --- SECTION 3: DAMPAK CUACA & KLASTERISASI ---
st.subheader("3. Dampak Cuaca & Klasterisasi Waktu Operasional vs Suhu")
c3, c4 = st.columns(2)

with c3:
    w_order = [w for w in ["Clear / Partly Cloudy", "Mist / Cloudy", "Light Snow / Rain", "Heavy Rain / Ice"] if w in hour_filtered["weather_label"].unique()]
    w_stats = hour_filtered.groupby("weather_label")["cnt"].mean().reindex(w_order)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    colors_w = ["#1f77b4", "#5dade2", "#f39c12", "#c0392b"][:len(w_order)]
    y_pos = np.arange(len(w_order))
    ax.barh(y_pos, w_stats.values, color=colors_w, height=0.55)
    ax.invert_yaxis()
    for i, v in enumerate(w_stats.values):
        ax.text(v + 3, i, f"{v:.1f}/jam", va="center", fontweight="bold", fontsize=9)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(w_order)
    ax.set_xlabel("Rata-rata Penyewaan / Jam")
    ax.set_xlim(0, max(w_stats.max() * 1.22, 50))
    ax.set_title("Rata-rata Penyewaan per Jam Menurut Cuaca")
    st.pyplot(fig)
    plt.close(fig)

with c4:
    cluster_order = ["Morning Peak (06-09)", "Daytime (10-15)", "Evening Peak (16-19)", "Night / Off-Peak (20-05)"]
    temp_order = ["Cold (<15°C)", "Mild (15-25°C)", "Warm (>25°C)"]
    pivot_cluster = hour_filtered.pivot_table(
        index="time_cluster",
        columns="temp_cluster",
        values="cnt",
        aggfunc="mean",
        observed=False
    ).reindex(index=cluster_order, columns=temp_order)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    sns.heatmap(pivot_cluster, annot=True, fmt=".1f", cmap="YlGnBu", linewidths=0.5, ax=ax)
    ax.set_title("Klasterisasi: Waktu Operasional vs Kategori Suhu")
    ax.set_xlabel("Kategori Suhu")
    ax.set_ylabel("Klaster Waktu")
    st.pyplot(fig)
    plt.close(fig)

st.caption("Sumber Data: Capital Bikeshare System (2011–2012), Washington D.C.")
