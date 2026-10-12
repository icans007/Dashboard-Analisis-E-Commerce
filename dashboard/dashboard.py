import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import streamlit as st

st.set_page_config(
    page_title="Dashboard Analisis E-Commerce",
    layout="wide"
)

INK = "#14213D"       
MUTED = "#6B7280"      
TEAL = "#0F766E"       
TEAL_SOFT = "#99D5CF"  
AMBER = "#F59E0B"      
GRID = "#E5E7EB"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.edgecolor": GRID,
    "axes.labelcolor": MUTED,
    "axes.titleweight": "bold",
    "axes.titlesize": 12,
    "axes.titlecolor": INK,
    "axes.titlelocation": "left",
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"], .stMarkdown, .stMetric, button, input {{
        font-family: 'Plus Jakarta Sans', sans-serif;
    }}

    .stApp {{ background: #F6F8FA; }}
    .block-container {{ padding-top: 2rem; padding-bottom: 3rem; max-width: 1400px; }}
    footer {{ visibility: hidden; }}

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] {{
        background: #FFFFFF;
        border-right: 1px solid {GRID};
    }}
    section[data-testid="stSidebar"] h2 {{
        font-size: 1.25rem; font-weight: 800; color: {INK};
    }}
    section[data-testid="stSidebar"] label p {{
        font-weight: 600; color: {INK}; font-size: 0.85rem;
    }}
    /* tag multiselect: teal, bukan merah */
    span[data-baseweb="tag"] {{
        background-color: #E6F4F2 !important;
        border-radius: 6px !important;
    }}
    span[data-baseweb="tag"] span {{ color: {TEAL} !important; font-weight: 600; }}
    span[data-baseweb="tag"] svg {{ fill: {TEAL} !important; }}

    /* ---------- Hero ---------- */
    .hero {{
        background: linear-gradient(120deg, {INK} 0%, #1F3A5F 60%, {TEAL} 140%);
        border-radius: 18px;
        padding: 2rem 2.25rem;
        margin-bottom: 1.5rem;
    }}
    .hero h1 {{
        color: #FFFFFF; font-size: 2.1rem; font-weight: 800;
        margin: 0 0 .35rem 0; padding: 0; letter-spacing: -0.02em;
    }}
    .hero p {{ color: #CBD5E1; margin: 0; font-size: 1rem; }}
    .hero .period {{
        display: inline-block; margin-top: 1rem;
        background: rgba(255,255,255,.12); color: #FFFFFF;
        padding: .3rem .8rem; border-radius: 999px; font-size: .82rem; font-weight: 600;
    }}

    /* ---------- KPI cards ---------- */
    .kpi {{
        background: #FFFFFF;
        border: 1px solid {GRID};
        border-left: 5px solid var(--accent);
        border-radius: 14px;
        padding: 1.1rem 1.25rem;
        height: 100%;
    }}
    .kpi .label {{ color: {MUTED}; font-size: .85rem; font-weight: 600; }}
    .kpi .value {{
        color: {INK}; font-size: 1.85rem; font-weight: 800;
        line-height: 1.25; margin-top: .25rem; word-break: break-word;
    }}
    .kpi .sub {{ color: {MUTED}; font-size: .78rem; margin-top: .15rem; }}

    /* ---------- Tabs ---------- */
    .stTabs [data-baseweb="tab-list"] {{ gap: .5rem; border-bottom: 1px solid {GRID}; }}
    .stTabs [data-baseweb="tab"] {{
        padding: .6rem 1.1rem; font-weight: 600; color: {MUTED};
        border-radius: 10px 10px 0 0;
    }}
    .stTabs [aria-selected="true"] {{ color: {TEAL} !important; }}
    .stTabs [data-baseweb="tab-highlight"] {{ background-color: {TEAL} !important; }}

    /* ---------- Container bergaris ---------- */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: #FFFFFF; border-radius: 14px; border-color: {GRID};
    }}

    h3 {{ color: {INK}; font-weight: 700; letter-spacing: -0.01em; }}

    /* ---------- Insight ---------- */
    .insight {{
        background: #FFFFFF; border: 1px solid {GRID};
        border-radius: 14px; padding: 1.1rem 1.25rem; height: 100%;
    }}
    .insight h4 {{ margin: 0 0 .5rem 0; color: {INK}; font-size: 1rem; font-weight: 700; }}
    .insight ul {{ margin: 0; padding-left: 1.1rem; color: #374151; font-size: .9rem; line-height: 1.6; }}
    .insight li {{ margin-bottom: .45rem; }}
    </style>
    """,
    unsafe_allow_html=True,
)


def kpi_card(label, value, sub="", accent=TEAL):
    st.markdown(
        f"""
        <div class="kpi" style="--accent:{accent}">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
            <div class="sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def compact(v):
    """Format angka besar agar tidak terpotong: 1.7M, 350K, dst."""
    if abs(v) >= 1e6:
        return f"{v / 1e6:.2f}M"
    if abs(v) >= 1e3:
        return f"{v / 1e3:.0f}K"
    return f"{v:,.0f}"


def clean_axes(ax, grid_axis="y"):
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.grid(axis=grid_axis, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)


def thin_xticks(ax, labels, max_ticks=8):
    step = max(1, len(labels) // max_ticks)
    idx = list(range(0, len(labels), step))
    ax.set_xticks(idx)
    ax.set_xticklabels([labels[i] for i in idx], rotation=35, ha="right")



# LOAD DATA

@st.cache_data
def load_data():
    df = pd.read_csv("dashboard/main_data.csv")
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    df["year"] = df["order_purchase_timestamp"].dt.year
    df["month"] = df["order_purchase_timestamp"].dt.month
    df["month_year"] = df["order_purchase_timestamp"].dt.to_period("M").astype(str)
    return df

df = load_data()


# SIDEBAR

with st.sidebar:
    st.header("Filter Data")
    st.caption("Sesuaikan rentang data yang ingin ditampilkan.")

    # Filter tanggal
    min_date = df["order_purchase_timestamp"].min().date()
    max_date = df["order_purchase_timestamp"].max().date()

    date_range = st.date_input(
        "Rentang tanggal",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    # Filter tahun
    available_years = sorted(df["year"].dropna().unique().tolist())
    selected_years = st.multiselect("Tahun", options=available_years, default=available_years)

    # Filter bulan
    month_map = {
        1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
        5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
        9: "September", 10: "Oktober", 11: "November", 12: "Desember"
    }
    available_months = sorted(df["month"].dropna().unique().tolist())
    selected_months = st.multiselect(
        "Bulan",
        options=available_months,
        default=available_months,
        format_func=lambda x: month_map.get(x, str(x))
    )

    # Filter kategori produk
    if "product_category_name" in df.columns:
        categories = sorted(df["product_category_name"].dropna().unique().tolist())
        selected_categories = st.multiselect(
            "Kategori produk",
            options=categories,
            default=categories[:10] if len(categories) > 10 else categories
        )
    else:
        selected_categories = []

    # Filter kota customer
    if "customer_city" in df.columns:
        cities = sorted(df["customer_city"].dropna().unique().tolist())
        selected_cities = st.multiselect(
            "Kota customer",
            options=cities,
            default=cities
        )
    else:
        selected_cities = []

    # Filter range payment
    min_payment = float(df["payment_value"].min())
    max_payment = float(df["payment_value"].max())

    payment_range = st.slider(
        "Rentang nilai pembayaran (R$)",
        min_value=float(min_payment),
        max_value=float(max_payment),
        value=(float(min_payment), float(max_payment))
    )

    # Pilihan jumlah top data
    top_n = st.slider("Jumlah top kategori", min_value=5, max_value=20, value=10)

    st.markdown("---")
    st.info("Gunakan filter di atas untuk melihat data yang lebih spesifik.")


# FILTER DATAFRAME

filtered_df = df[
    (df["order_purchase_timestamp"].dt.date >= start_date) &
    (df["order_purchase_timestamp"].dt.date <= end_date) &
    (df["year"].isin(selected_years)) &
    (df["month"].isin(selected_months)) &
    (df["payment_value"].between(payment_range[0], payment_range[1]))
]

if "product_category_name" in filtered_df.columns and len(selected_categories) > 0:
    filtered_df = filtered_df[filtered_df["product_category_name"].isin(selected_categories)]

if "customer_city" in filtered_df.columns and len(selected_cities) > 0:
    filtered_df = filtered_df[filtered_df["customer_city"].isin(selected_cities)]


# HEADER & METRICS

st.markdown(
    f"""
    <div class="hero">
        <h1>Dashboard Analisis E-Commerce</h1>
        <p>Performa transaksi, tren penjualan, dan segmentasi pelanggan dalam satu tampilan.</p>
        <span class="period">Periode: {start_date:%d %b %Y} – {end_date:%d %b %Y}</span>
    </div>
    """,
    unsafe_allow_html=True,
)

if filtered_df.empty:
    st.warning("Tidak ada data yang sesuai dengan filter yang dipilih. Silakan sesuaikan filter di menu *sidebar*.")
    st.stop()

# Menampilkan metrik utama
total_orders = filtered_df["order_id"].nunique()
total_revenue = filtered_df["payment_value"].sum()
total_customers = filtered_df["customer_id"].nunique()
top_category = filtered_df["product_category_name"].mode()[0] if "product_category_name" in filtered_df.columns else "-"

col1, col2, col3, col4 = st.columns(4)
with col1:
    kpi_card("Total Orders", f"{total_orders:,}", "Order unik", TEAL)
with col2:
    kpi_card("Total Revenue", f"R$ {compact(total_revenue)}", f"R$ {total_revenue:,.2f}", AMBER)
with col3:
    kpi_card("Total Customers", f"{total_customers:,}", "Customer unik", "#3B82F6")
with col4:
    kpi_card("Top Category", str(top_category).replace("_", " ").title(), "Kategori dengan penjualan terbanyak", "#8B5CF6")

st.markdown("<br>", unsafe_allow_html=True)

# VISUALISASI UTAMA (MENGGUNAKAN TABS)\
tab1, tab2, tab3 = st.tabs(["Performa Produk", "Tren Penjualan", "Segmentasi Pelanggan (RFM)"])

with tab1:
    with st.container(border=True):
        st.subheader(f"Top {top_n} Kategori Produk Terlaris")
        top_products = (
            filtered_df["product_category_name"]
            .value_counts()
            .head(top_n)
        )
        labels = [str(i).replace("_", " ") for i in top_products.index]
        colors = [TEAL] + [TEAL_SOFT] * (len(top_products) - 1)

        fig, ax = plt.subplots(figsize=(10, max(4, top_n * 0.45)))
        bars = ax.barh(labels, top_products.values, color=colors, height=0.65)
        ax.invert_yaxis()
        ax.set_xlabel("Jumlah Penjualan")
        clean_axes(ax, grid_axis="x")
        ax.yaxis.grid(False)
        for bar, v in zip(bars, top_products.values):
            ax.text(v + top_products.max() * 0.01, bar.get_y() + bar.get_height() / 2,
                    f"{v:,}", va="center", fontsize=9, color=INK, fontweight="bold")
        ax.set_xlim(0, top_products.max() * 1.12)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

with tab2:
    st.subheader("Tren Order dan Revenue Bulanan")
    col_trend1, col_trend2 = st.columns(2)

    with col_trend1:
        with st.container(border=True):
            monthly_orders = (
                filtered_df.groupby("month_year")["order_id"]
                .nunique()
                .sort_index()
            )
            x = list(range(len(monthly_orders)))
            fig, ax = plt.subplots(figsize=(8, 4.5))
            ax.plot(x, monthly_orders.values, marker="o", color=TEAL, linewidth=2.5, markersize=5)
            ax.fill_between(x, monthly_orders.values, color=TEAL, alpha=0.12)
            peak = monthly_orders.values.argmax()
            ax.scatter(peak, monthly_orders.values[peak], color=AMBER, s=90, zorder=5)
            ax.annotate(f"Puncak: {monthly_orders.values[peak]:,}",
                        (peak, monthly_orders.values[peak]),
                        textcoords="offset points", xytext=(0, 12), ha="center",
                        fontsize=9, color=INK, fontweight="bold")
            ax.set_title("Tren Order Bulanan")
            ax.set_ylabel("Jumlah Order")
            ax.set_ylim(0, monthly_orders.max() * 1.18)
            clean_axes(ax)
            thin_xticks(ax, list(monthly_orders.index))
            fig.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

    with col_trend2:
        with st.container(border=True):
            monthly_revenue = (
                filtered_df.groupby("month_year")["payment_value"]
                .sum()
                .sort_index()
            )
            x = list(range(len(monthly_revenue)))
            fig, ax = plt.subplots(figsize=(8, 4.5))
            ax.plot(x, monthly_revenue.values, marker="o", color=AMBER, linewidth=2.5, markersize=5)
            ax.fill_between(x, monthly_revenue.values, color=AMBER, alpha=0.15)
            peak = monthly_revenue.values.argmax()
            ax.scatter(peak, monthly_revenue.values[peak], color=TEAL, s=90, zorder=5)
            ax.annotate(f"Puncak: R$ {compact(monthly_revenue.values[peak])}",
                        (peak, monthly_revenue.values[peak]),
                        textcoords="offset points", xytext=(0, 12), ha="center",
                        fontsize=9, color=INK, fontweight="bold")
            ax.set_title("Revenue Bulanan")
            ax.set_ylabel("Total Revenue (R$)")
            ax.set_ylim(0, monthly_revenue.max() * 1.18)
            ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: compact(v)))
            clean_axes(ax)
            thin_xticks(ax, list(monthly_revenue.index))
            fig.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

with tab3:
    with st.container(border=True):
        st.subheader("Distribusi RFM Score")
        snapshot_date = filtered_df["order_purchase_timestamp"].max()

        rfm = filtered_df.groupby("customer_id").agg({
            "order_purchase_timestamp": lambda x: (snapshot_date - x.max()).days,
            "order_id": "nunique",
            "payment_value": "sum"
        }).reset_index()

        rfm.columns = ["customer_id", "Recency", "Frequency", "Monetary"]

        if not rfm.empty and len(rfm) >= 4:
            rfm["R_score"] = pd.qcut(rfm["Recency"], 4, labels=[4, 3, 2, 1], duplicates="drop")
            rfm["F_score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4], duplicates="drop")
            rfm["M_score"] = pd.qcut(rfm["Monetary"], 4, labels=[1, 2, 3, 4], duplicates="drop")
            rfm["RFM_score"] = (
                rfm["R_score"].astype(int) +
                rfm["F_score"].astype(int) +
                rfm["M_score"].astype(int)
            )

            dist = rfm["RFM_score"].value_counts().sort_index()
            colors = [AMBER if v == dist.max() else TEAL_SOFT for v in dist.values]

            fig, ax = plt.subplots(figsize=(10, 4.5))
            bars = ax.bar(dist.index.astype(str), dist.values, color=colors, width=0.65)
            ax.set_xlabel("RFM Score")
            ax.set_ylabel("Jumlah Customer")
            clean_axes(ax)
            for bar, v in zip(bars, dist.values):
                ax.text(bar.get_x() + bar.get_width() / 2, v + dist.max() * 0.01,
                        f"{v:,}", ha="center", va="bottom", fontsize=9, color=INK, fontweight="bold")
            ax.set_ylim(0, dist.max() * 1.12)
            fig.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
        else:
            st.warning("Data tidak cukup untuk menampilkan distribusi RFM berdasarkan filter saat ini.")

st.markdown("<br>", unsafe_allow_html=True)


# DATA PREVIEW & INSIGHTS

col_data, col_insight = st.columns([1.5, 1])

with col_data:
    with st.expander("Lihat Data Mentah (Preview)"):
        st.dataframe(filtered_df.head(50), use_container_width=True)

with col_insight:
    st.markdown(
        """
        <div class="insight">
            <h4> Insight Utama</h4>
            <ul>
                <li>Kategori terlaris di <b>Performa Produk</b> dapat memandu prioritas restok dan strategi promosi.</li>
                <li>Pola di <b>Tren Penjualan</b> membantu mengenali musim ramai (peak season) dan musim sepi.</li>
                <li>Distribusi <b>RFM Score</b> memisahkan pelanggan loyal dari pelanggan yang berisiko churn.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )